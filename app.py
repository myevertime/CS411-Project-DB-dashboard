import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import mysql.connector
import pandas as pd

# Create the Dash app
group_colors = {"control": "light blue", "reference": "red"}

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Connect to the MySQL database (Make sure to update the credentials)
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='test_root',
    database='academicworld'
)

## I don't know why but these code blocks keeps connecting the website
## I'm figuring out on this - asked TA for help
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
app.layout = html.Div(
    children=[
        # Top Banner
        html.Div(
            className="study-browser-banner row",
            children=[
                html.H2(className="h2-title", children="University Explorer: Find your best-fit ML/AI University"),
                html.H2(className="h2-title-mobile", children="University Explorer"),
                #html.P("")
            ],
        ),
        # Body of the App
        html.Div(
            className="row app-body",
            children=[
                # User Controls
                html.Div(
                    className="five columns card",
                    children=[
                        html.Div(
                            className="bg-white user-control",
                            children=[
                                html.Div(
                                    className="padding-top-bot",
                                    children=[
                                        html.H6("Keyword"),
                                        dcc.Dropdown(
                                            id='keyword-filter',
                                            options=[{'label': keyword, 'value': keyword} for keyword in keywords],
                                            placeholder='Select a domain that you\'re interested in',
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            className="bg-white2",
                            children=[
                                html.H6("Top 5 keyword-matched universities"),
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
                                )
                            ],
                        ),
                        html.Div(
                            className="bg-white2",
                            children=[
                                html.H6("Top 5 keyword-matched faculties"),
                                dash_table.DataTable(
                                    id='keyword-univ-table2',
                                    columns=[
                                        {'name': 'Faculty', 'id': 'fac_name'},
                                        {'name': 'University', 'id': 'univ_name'},
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
                                )
                            ],
                        )
                    ],
                ),
                # Table
                html.Div(
                    className="eight columns card-left",
                    children=[
                        ##
                    ],
                ),
                #dcc.Store(id="error", storage_type="memory"),
            ],
        ),
    ]
)

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
    filtered_df = filtered_df.sort_values('KRC', ascending=False)[:5]

    # Prepare data for the table
    table_data = [{'univ_name': row['university_name'], 'fac_cnt': row['fac_cnt'], 'pub_cnt':row['pub_cnt'], 'KRC':row['KRC']} for _, row in filtered_df.iterrows()]
    return table_data


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
