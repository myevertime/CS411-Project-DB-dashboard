import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import mysql.connector

# Create the Dash app
app = dash.Dash(__name__)

# Connect to the MySQL database (Make sure to update the credentials)
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='test_root',
    database='academicworld'
)

# Get the list of unique university names from the database
cursor = db_connection.cursor()
cursor.execute("SELECT DISTINCT name FROM university")
universities = cursor.fetchall()
universities = [uni[0] for uni in universities]
cursor.close()

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("University Explorer: Find Your Best-fit ML/AI University"),

    dcc.Dropdown(
        id='university-filter',
        options=[{'label': uni, 'value': uni} for uni in universities],
        placeholder='Select a University',
    ),
    
    dash_table.DataTable(
        id='university-table',
        columns=[
            {'name': 'University', 'id': 'university_name'},
            {'name': 'Count', 'id': 'numeric_feature_1'}
            # Add more columns for other numeric features as needed
        ],
        # Set the style properties for the table
        style_table={'overflowX': 'auto'},
        style_cell={
            'height': 'auto',
            'minWidth': '0px', 'maxWidth': '180px',
            'whiteSpace': 'normal'
        }
    ),
])

# Define the callback function to update the table based on the university filter input
@app.callback(
    Output('university-table', 'data'),
    [Input('university-filter', 'value')]
)
def update_table(selected_university):
    # Fetch data from the MySQL database based on the selected university
    cursor = db_connection.cursor()
    query = f"""SELECT univ.name, count(faculty.id) from (
        select id, name from university) as univ 
        inner join (select id, university_id from faculty) as faculty 
        on univ.id = faculty.university_id
        group by univ.name"""

    # Apply the filter if a university is selected
    if selected_university:
        query += f" HAVING univ.name = '{selected_university}'"

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    # Prepare data for the table
    table_data = [{'university_name': row[0], 'numeric_feature_1': row[1]} for row in result]
    return table_data


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
