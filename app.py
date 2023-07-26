import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import mysql.connector
import pandas as pd

# Create the Dash app
app = dash.Dash(__name__)

# Connect to the MySQL database (Make sure to update the credentials)
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='test_root',
    database='academicworld'
)

## I don't know why but these code blocks keeps connecting the website
#---------------------------------
## Get the list of keywords by running keyword creation SQL file
#with open('sql/createKeywordView.sql', 'r') as f:
#    with db_connection.cursor() as cursor:
#        cursor.execute(f.read(), multi=True)
#    db_connection.commit()
#with open('sql/createKeywordUnivView.sql', 'r') as f:
#    with db_connection.cursor() as cursor:
#        sql_statements = f.read().split(';')
#        for statement in sql_statements:
#            cursor.execute(statement)
#    db_connection.commit()

cursor = db_connection.cursor()
cursor.execute("SELECT name FROM keywordView")
keywords = cursor.fetchall()
keywords = [keyword[0] for keyword in keywords]
cursor.close()

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("University Explorer: Find your best-fit ML/AI University"),

    dcc.Dropdown(
        id='keyword-filter',
        options=[{'label': keyword, 'value': keyword} for keyword in keywords],
        placeholder='Select a domain that you\'re interested in',
    ),
    
    dash_table.DataTable(
        id='keyword-univ-table',
        columns=[
            {'name': 'University', 'id': 'univ_name'},
            {'name': 'Faculty Count', 'id': 'fac_cnt'},
            {'name': 'Publications Count', 'id': 'pub_cnt'},
            {'name': 'KRC', 'id': 'KRC'}
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
    Output('keyword-univ-table', 'data'),
    [Input('keyword-filter', 'value')]
)
def update_table(keyword):
    # Fetch data from the MySQL database based on the selected university
    cursor = db_connection.cursor()
    query = "SELECT * FROM keyword_univ_final"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    df = pd.DataFrame(result)
    df.columns = ['university_name', 'keyword_name', 'fac_cnt', 'pub_cnt', 'KRC']
    filtered_df = df[df['keyword_name'] == keyword][['university_name', 'fac_cnt', 'pub_cnt', 'KRC']]
    filtered_df = filtered_df.sort_values('KRC', ascending=False)

    # Prepare data for the table
    table_data = [{'univ_name': row['university_name'], 'fac_cnt': row['fac_cnt'], 'pub_cnt':row['pub_cnt'], 'KRC':row['KRC']} for _, row in filtered_df.iterrows()]
    return table_data


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
