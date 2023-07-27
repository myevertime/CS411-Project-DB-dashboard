from utils import *
from mysql_utils import *
from mongodb_utils import *
from neo4j_utils import *

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Link the custom CSS file
#app.css.append_css({"external_url": "assets/custom.css"})

mysql = mysql_connector()
mongodb = mongodb_connector()

# Fetch data from MongoDB and convert to DataFrame
collection = mongodb['faculty']
pipeline = [
    {'$unwind': '$keywords'},
    {'$sort': {'keywords.score': -1}},
    {'$group': {
        '_id': '$_id',
        'name': {'$first': '$name'},
        'position': {'$first': '$position'},
        'email': {'$first': '$email'},
        'phone': {'$first': '$phone'},
        'affiliation': {'$first': '$affiliation.name'},
        'photoUrl': {'$first': '$photoUrl'},
        'Top Keyword': {'$first': '$keywords.name'},
        #'Keyword Score': {'$first': '$keywords.score'}
    }},
    {'$project': {'_id': 0, 'name': 1, 'position': 1, 'email': 1, 'phone': 1, 'affiliation': 1, 'photoUrl': 1, 'Top Keyword': 1}} #'Keyword Score': 1
]
data_from_mongo = list(collection.aggregate(pipeline))
mongodb_df = pd.DataFrame(data_from_mongo)

## Get the list of keywords by running keyword creation SQL file
sql_lst = []
with open('sql/createBaseTables.sql', 'r') as f:
    sql_statements = f.read().split(';')
    for statement in sql_statements:
        if statement != "":
            sql_lst.append(statement)
        #cursor.execute(statement)

cursor = mysql.cursor()
for statement in sql_lst:
    cursor.execute(statement)
    mysql.commit()
cursor.close()

cursor = mysql.cursor()
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
        # Second body of the App - Keyword Section
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
                                        html.H4("Search By Areas"),
                                        dcc.Dropdown(
                                            id='keyword-filter',
                                            options=[{'label': keyword, 'value': keyword} for keyword in keywords],
                                            placeholder='Select the area that you\'re interested in',
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            className="bg-white2",
                            children=[
                                html.H6("Top 5 matched universities"),
                                dash_table.DataTable(
                                    id='keyword-univ-table',
                                    columns=[
                                        {'name': 'University', 'id': 'univ_name'},
                                        {'name': 'Faculty', 'id': 'fac_cnt'},
                                        {'name': 'Publications', 'id': 'pub_cnt'},
                                        {'name': 'KRC', 'id': 'KRC'}
                                        # Add more columns for other numeric features as needed
                                    ],
                                    # Set the style properties for the table
                                    style_table={'overflowX': 'auto'},
                                    style_cell={
                                        'height': 'auto',
                                        'width': 'auto',
                                        'minWidth': '0px', 'maxWidth': '180px',
                                        'whiteSpace': 'normal'
                                    },
                                    style_header={
                                        'fontWeight': 'bold',
                                    },
                                    style_data_conditional=[
                                        {
                                        'if': {'row_index': 0},
                                        'backgroundColor': 'lightyellow',
                                        'fontWeight': 'bold',
                                        },
                                    ],
                                )
                            ],
                        ),
                        html.Div(
                            className="bg-white2",
                            children=[
                                html.H6("Top 5 matched faculties"),
                                dash_table.DataTable(
                                    id='keyword-faculty-table',
                                    columns=[
                                        {'name': 'Name', 'id': 'fac_name'},
                                        {'name': 'University', 'id': 'univ_name'},
                                        {'name': 'Publications', 'id': 'pub_cnt'},
                                        {'name': 'KRC', 'id': 'KRC'}
                                        # Add more columns for other numeric features as needed
                                    ],
                                    # Set the style properties for the table
                                    style_table={'overflowX': 'auto'},
                                    style_cell={
                                        'height': 'auto',
                                        'width': 'auto',
                                        'minWidth': '0px', 'maxWidth': '180px',
                                        'whiteSpace': 'normal'
                                    },
                                    style_header={
                                        'fontWeight': 'bold',
                                    },
                                    style_data_conditional=[
                                        {
                                        'if': {'row_index': 0},
                                        'backgroundColor': 'lightyellow',
                                        'fontWeight': 'bold',
                                        },
                                    ],
                                )
                            ],
                        ),
                        html.Div(
                            className="bg-white3",
                            children=[
                                html.H6("Update New Area"),
                                dcc.Input(
                                        id='update-keyword',
                                        type='text',
                                        placeholder='Interested in other area?',
                                        style = {'width':'300px', 'margin-right': '15px'} 
                                ),
                                html.Button('Update', id='update-button', n_clicks=0, style={'display':'right'}),
                            ]
                        ),
                        # ConfirmDialog to show a pop-up when the update is successful
                        dcc.ConfirmDialog(
                            id='update-success-popup',
                            message='Update successful! We will start to collect new data that you gave, so stay tuned! :)',
                        ),
                    ],
                ),
                # Second body of the App - University Section
                html.Div(
                    className="seven columns card-left",
                    children=[
                        html.Div(
                            className="bg-white user-control",
                            children=[
                                html.Div(
                                    className="padding-top-bot",
                                    children=[
                                        html.H4("Search By University"),
                                        ##
                                    ]
                                )
                            ]
                        )
                    ],
                ),
                # Third body of the App - Professor Section
                html.Div(
                    className="seven columns card-left",
                    children=[
                        html.Div(
                            className="bg-white user-control",
                            children=[
                                html.Div(
                                    className="padding-top-bot",
                                    children=[
                                        html.H4("Search By Professor"),
                                        # Dropdown to select the key for filtering
                                        dcc.Dropdown(
                                            id='filter-key',
                                            options=[{'label': name, 'value': name} for name in list(mongodb_df['name'])],
                                            value = 'Neel Sundaresan',
                                            placeholder='Select the professor that you\'re interested in',
                                            style = {'width':'350px'} 
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            className="bg-white2",
                            children=[
                                # Bar chart to display filtered data
                                html.Img(id="professor-img",src="", style={"width": "150px", "height": "200px", "border-radius": "80% / 50%", "margin-right": "20px"}),
                                dcc.Markdown(
                                    id="key-value-textarea",
                                    children="",
                                    style={"width": "100%", "height": "200px", "border":"None", "outline":"None","line-height": "1.5", "font-family":"verdana"},
                                    dangerously_allow_html=True,
                                ),
                            ], style={"display": "flex"}
                        ),
                    ]
                ),
            ],
        ),
    ]
)

# Define the callback function to update the table based on the university filter input
@app.callback(
    [Output('keyword-univ-table', 'data'),
    Output('keyword-faculty-table', 'data'),
    Output('update-keyword', 'value'),
    Output('update-success-popup', 'displayed'),
    Output("key-value-textarea", "children"),
    Output("professor-img", "src")],
    [Input('keyword-filter', 'value'),
    Input('update-button', 'n_clicks'),
    Input('filter-key', 'value')],
    [State('update-keyword', 'value')]
)
def update_table(keyword, n_clicks, filter_key, update_keyword_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    success_popup_displayed = False

    ## First Table: keyword filter on university list
    cursor = mysql.cursor()
    query = "SELECT * FROM keyword_univ_final"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    df = pd.DataFrame(result)
    df.columns = ['university_name', 'keyword_name', 'fac_cnt', 'pub_cnt', 'KRC']
    filtered_df = df[df['keyword_name'] == keyword][['university_name', 'fac_cnt', 'pub_cnt', 'KRC']]
    filtered_df = filtered_df.sort_values('KRC', ascending=False)[:5]

    table_data1 = [{'univ_name': row['university_name'], 'fac_cnt': row['fac_cnt'], 'pub_cnt':row['pub_cnt'], 'KRC':row['KRC']} for _, row in filtered_df.iterrows()]
    
    ## Second Table: keyword filter on faculty list
    cursor = mysql.cursor()
    query = "SELECT * FROM keyword_faculty_final"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    df2 = pd.DataFrame(result)
    df2.columns = ['fac_name', 'univ_name', 'keyword_name', 'pub_cnt', 'KRC']
    filtered_df2 = df2[df2['keyword_name'] == keyword][['fac_name', 'univ_name', 'pub_cnt', 'KRC']]
    filtered_df2 = filtered_df2.sort_values('KRC', ascending=False)[:5]

    table_data2 = [{'fac_name': row['fac_name'], 'univ_name': row['univ_name'], 'pub_cnt':row['pub_cnt'], 'KRC':row['KRC']} for _, row in filtered_df2.iterrows()]
    
    # Check which input triggered the callback
    if trigger_id == 'update-button':
        # Update the database with the user keyword input from the web UI
        cursor = mysql.cursor()
        query = "SELECT max(id) FROM keyword"
        cursor.execute(query)
        max_id = cursor.fetchall()
        query = f"INSERT INTO keyword VALUES({max_id[0][0]+1},'{update_keyword_value}')"
        cursor.execute(query)
        mysql.commit()
        cursor.close()

        success_popup_displayed = True
    
    # professor section
    mongo_data = ""
    photoUrl = ""
    for json_ in data_from_mongo:
        if json_['name'] == filter_key:
            photoUrl = json_['photoUrl']
            for key, value in json_.items():
                if key != 'photoUrl' and not type(value) is NoneType:
                    if value != "":
                        mongo_data += f"🔹 <b>{key.capitalize()} : </b> {value.title()}<br>"

    return table_data1, table_data2, '', success_popup_displayed, mongo_data, photoUrl

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
