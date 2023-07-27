import sys
sys.path.append("utils/")
from utils import *
from mysql_utils import *
from mongodb_utils import *
from neo4j_utils import *

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_cytoscape as cyto

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

mysql = mysql_connector()
mongodb = mongodb_connector()


##-------------------------
# Create Base Tables
sql_lst = []
with open('sql/createBaseTables.sql', 'r') as f:
    sql_statements = f.read().split(';')
    for statement in sql_statements:
        if statement != "":
            sql_lst.append(statement)
cursor = mysql.cursor()
for statement in sql_lst:
    cursor.execute(statement)
    mysql.commit()
cursor.close()

##-------------------------
# Get query result from MongoDB
data_from_mongo, mongodb_df = mongodb_query_result(mongodb)

##-------------------------
## Get the list of keywords by running keyword creation SQL file
cursor = mysql.cursor()
cursor.execute("SELECT name FROM keywordView")
keywords = cursor.fetchall()
keywords = [keyword[0] for keyword in keywords]
cursor.close()

##-------------------------
# Define the layout of the dashboard
app.layout = html.Div(
    children=[
        # Top Banner
        html.Div(
            className="study-browser-banner row",
            children=[
                html.H2(className="h2-title", children="University Explorer: Find your best-fit ML/AI University"),
                html.H2(className="h2-title-mobile", children="University Explorer"),
                html.P("This website offers you the opportunity to explore the best-fit university for you, taking into account various aspects. Take your time to discover the perfect university match.")
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
                                            options=[{'label': keyword.title(), 'value': keyword} for keyword in keywords],
                                            value = 'computer vision',
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
                                    ],
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
                                    ],
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
                                            options=[{'label': name.title(), 'value': name} for name in list(mongodb_df['name'])],
                                            value = 'Nam Wook Kim',
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
                                html.Img(id="professor-img",src="", style={"width": "100px", "height": "150px", "border-radius": "80% / 50%", "margin-right": "20px"}),
                                dcc.Markdown(
                                    id="key-value-textarea",
                                    children="",
                                    style={"width": "100%", "height": "150px", "border":"None", "outline":"None","line-height": "1.5", "font-family":"verdana"},
                                    dangerously_allow_html=True,
                                ),
                            ], style={"display": "flex"}
                        ),
                        cyto.Cytoscape(
                            id='cytoscape-network',
                            layout={'name': 'cose'},
                            elements=[],
                            style={'height': '200px', 'width':'800px'},
                            stylesheet=[
                                {
                                    'selector': 'node, edge',
                                    'style': {
                                        'background-color': 'white'
                                    }
                                },
                                # Style for nodes (hide node labels)
                                {
                                    'selector': 'node',
                                    'style': {
                                        'label': '',  # Hide node labels
                                        'width': '25px',  # Set the node size
                                        'height': '25px',
                                    }
                                },
                                # Style for edges (show edge labels)
                                {
                                    'selector': 'edge[label]',
                                    'style': {
                                        'label': 'data(label)',  # Show edge labels
                                        'width':3,
                                        'font-size':'15px',
                                        "text-background-opacity": 0.2,
                                        "text-background-color": "#fff",
                                        'curve-style': 'bezier',
                                        'target-arrow-shape': 'triangle'
                                    }
                                },
                                {
                                    'selector': '.institute',
                                    'style': {
                                        'background-color': '#aec7e8',  # Light blue
                                        'line-color': '#aec7e8'
                                    }
                                },
                                {
                                    'selector': '.faculty',
                                    'style': {
                                        'background-color': '#1f77b4',  # blue
                                        'line-color': '#1f77b4'
                                    }
                                },
                                {
                                    'selector': '.keyword',
                                    'style': {
                                        'background-color': '#98df8a',  # Greenish blue
                                        'line-color': '#98df8a'
                                    }
                                },
                                {
                                    'selector': '.publication',
                                    'style': {
                                        'background-color': '#9edae5',  # Blueish green
                                        'line-color': '#9edae5'
                                    }
                                },
                            ]
                        ),
                        # Legend for node colors
                        html.Div(
                            className='legend',
                            children=[
                                html.Div(
                                    className='legend-item',
                                    children=[
                                        html.Span(className='legend-circle', style={'background-color': '#1f77b4'}),
                                        html.Span('Faculty', className='legend-label')
                                    ]
                                ),
                                html.Div(
                                    className='legend-item',
                                    children=[
                                        html.Span(className='legend-circle', style={'background-color': '#aec7e8'}),
                                        html.Span('Institute', className='legend-label')
                                    ]
                                ),
                                html.Div(
                                    className='legend-item',
                                    children=[
                                        html.Span(className='legend-circle', style={'background-color': '#98df8a'}),
                                        html.Span('Keyword', className='legend-label')
                                    ]
                                ),
                                html.Div(
                                    className='legend-item',
                                    children=[
                                        html.Span(className='legend-circle', style={'background-color': '#9edae5'}),
                                        html.Span('Publication', className='legend-label')
                                    ]
                                )
                            ], style={'display': 'flex', 'flex-direction': 'row'}
                        ),
                        html.Pre(id='cytoscape-tapNodeData', style={'border': 'thin lightgrey solid','overflowX': 'auto'}),
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
    Output('update-success-popup', 'displayed'),],
    [Input('keyword-filter', 'value'),
    Input('update-button', 'n_clicks'),],
    [State('update-keyword', 'value')]
)
def keyword_section(keyword, n_clicks, update_keyword_value):
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
    
    ## Check which input triggered the callback
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
    
    return table_data1, table_data2, '', success_popup_displayed

@app.callback(
    Output('cytoscape-tapNodeData', 'children'),
    Input('cytoscape-network', 'mouseoverNodeData'),
)
def update_professor_graphproperty(node_data):
    if node_data:
        property = """"""
        # Display the properties as a JSON string (customize this display as needed)
        for key, value in node_data.items():
            if not type(value) is NoneType:
                if value != "" and value != "nan":
                    property += f"🔹 {key.capitalize()} : {value}\n"
    else:
        property = "Hover over a node to see its properties."
    return property

@app.callback(
    [Output("key-value-textarea", "children"),
    Output("professor-img", "src"),
    Output('cytoscape-network', 'elements'),],
    [Input('filter-key', 'value'),]
)
def update_professor(filter_key):
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
    if filter_key:
        # professor section - network graph
        elements = draw_networkgraph(filter_key)
    return mongo_data, photoUrl, elements

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
