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

#connection_pool = mysql_connector_pool()
mysqldb = mysql_connector()
mongodb = mongodb_connector()

##-------------------------
# Create Base Tables
sql_lst = []
with open('sql/createTables.sql', 'r') as f:
    sql_statements = f.read().split(';')
    for statement in sql_statements:
        if statement.strip() != "":
            sql_lst.append(statement)

cursor = mysqldb.cursor()
for statement in sql_lst:
    cursor.execute(statement)
    mysqldb.commit()
cursor.close()

##-------------------------
# Parallel Execution of SQL queries
#max_threads = 4
# Execute SQL statements in parallel using ThreadPoolExecutor
#with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
#    futures = [executor.submit(execute_sql_statement, connection_pool, statement) for statement in sql_lst]
# Wait for all tasks to complete
#concurrent.futures.wait(futures)
## Above code produces table locks by using same connections


##-------------------------
# Get query result from MongoDB
data_from_mongo, mongodb_df = mongodb_query_result(mongodb)

##-------------------------
## Get the list of keywords by running keyword creation SQL file
cursor = mysqldb.cursor()
cursor.execute("SELECT name FROM keywordView")
keywords = cursor.fetchall()
keywords = [keyword[0] for keyword in keywords]
cursor.close()

## Get the count for KPI charts
cursor = mysqldb.cursor()
cursor.execute("SELECT * FROM kpi_faculty")
kpi_faculty = cursor.fetchall()[0][0]
cursor.close()

cursor = mysqldb.cursor()
cursor.execute("SELECT * FROM kpi_publication")
kpi_publication = cursor.fetchall()[0][0]
cursor.close()

cursor = mysqldb.cursor()
cursor.execute("SELECT * FROM kpi_university")
kpi_university = cursor.fetchall()[0][0]
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
                html.P(className="sub-title", children="This website offers you the opportunity to explore the best-fit university for you, taking into account various aspects.") #Take your time to discover the perfect university match.
            ],
        ),
        html.H4("Current Database Size", style={'font-weight': 'bold', 'margin-left':'20px'}),
        html.Div(
            [
                html.Div([
                    html.H6("Number of Faculties", style={'text-align': 'center'}),
                    dcc.Graph(
                        id='professors-kpi', 
                        figure={
                            'data': [{
                                'type': 'indicator',
                                'value': kpi_faculty,
                                'number': {'valueformat': ',', 'font': {'size': 20}},
                                'mode': 'number'
                            }],
                            'layout': {"height": 30, 'paper_bgcolor':'rgba(0,0,0,0)','plot_bgcolor':'rgba(0,0,0,0)'} #'layout': {'title': 'Number of Faculties'}
                        },
                    )
                ], className='kpi-card'),
                html.Div([
                    html.H6("Number of Universities", style={'text-align': 'center'}),
                    dcc.Graph(
                        id='universities-kpi',
                        figure={
                            'data': [{
                                'type': 'indicator',
                                'value': kpi_university,
                                'number': {'valueformat': ',', 'font': {'size': 20}},
                                'mode': 'number'
                            }],
                            'layout': {"height": 30, 'paper_bgcolor':'rgba(0,0,0,0)','plot_bgcolor':'rgba(0,0,0,0)'} #'title': 'Number of Universities'}
                        },
                    )
                ], className='kpi-card'),
                html.Div([
                    html.H6("Number of Publications", style={'text-align': 'center'}),
                    dcc.Graph(
                        id='publication-kpi',
                        figure={
                            'data': [{
                                'type': 'indicator',
                                'value': kpi_publication,
                                'number': {'valueformat': ',', 'font': {'size': 20}},
                                'mode': 'number'
                            }],
                            'layout': {"height": 30, 'paper_bgcolor':'rgba(0,0,0,0)','plot_bgcolor':'rgba(0,0,0,0)'} #'layout': {'title': 'Number of Universities'}
                        },
                        style={'backgroundColor': 'transparent'}
                    )
                ], className='kpi-card'),
            ], className='kpi-container'
        ),
        # First body of the App - Keyword Section
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
                                            value = '',
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
                            className="update-keyword",
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
                        # FailDialog to show a pop-up when the update is unsuccessful
                        dcc.ConfirmDialog(
                            id='update-fail-popup',
                            message='Update Failed! You should insert more than 3 characters',
                        ),
                    ],
                ),
                # Second body of the App - Professor Section
                html.Div(
                    className="seven columns card-left",
                    children=[
                        html.Div(
                            className="bg-white3",
                            children=[
                                html.Div(
                                    className="bg-white",
                                    children=[
                                        html.H4("Search By Professor"),
                                        # Dropdown to select the key for filtering
                                        html.Div(
                                            #className="",
                                            children=[
                                                html.Div(
                                                    children = [
                                                        dcc.Dropdown(
                                                            id='filter-key',
                                                            options=[{'label': name.title(), 'value': name} for name in list(mongodb_df['name'])],
                                                            value = '',
                                                            placeholder='Search the professor name',
                                                            style = {'width':'350px', 'margin-bottom':'20px', 'margin-right':'15px'} 
                                                        ),
                                                        html.H6("Explore the network information of the professor."),
                                                    ], style={"display": "flex"} 
                                                ),
                                                html.Div(
                                                    #className="bg-white3",
                                                    children=[
                                                        html.Img(id="professor-img",src="assets/No-Image-Placeholder.png", style={"width": "100px", "height": "150px", "border-radius": "80% / 50%", "margin-right": "20px"}),
                                                        dcc.Markdown(
                                                            id="key-value-textarea",
                                                            children="",
                                                            style={"width": "300px", "height": "200px", "border":"None", "outline":"None","line-height": "1.5", "font-family":"verdana"},
                                                            dangerously_allow_html=True,
                                                        ),
                                                    ], style={"display": "flex"}
                                                ),
                                                html.Div(
                                                    id="publications-section",
                                                    className="publication user-control",
                                                    style={"max-height": "500px", "overflow-y": "auto"},
                                                    children=[
                                                        html.H5("Latest Publications"),
                                                        dcc.Markdown(id="publications-text", children="")
                                                    ]
                                                ),
                                                html.Div(
                                                    id="summary-section",
                                                    className="summary user-control",
                                                    children=[
                                                        html.H5("Summary by ChatGPT"),
                                                        dcc.Markdown(id="summary-text", children="")
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            className="bg-white4 custom-background",
                            children=[
                                html.Div(
                                    className="padding-top-bot cytograph",
                                    children=[
                                        cyto.Cytoscape(
                                            id='cytoscape-network',
                                            layout={'name': 'circle'},
                                            elements=[],
                                            style={'height': '400px', 'width':'400px'},
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
                                                        'label': 'data(label)',  # Hide node labels
                                                        'font-size':'25px',
                                                        'text-wrap': 'wrap',
                                                        'text-max-width':'100px',
                                                        'text-valign': 'center',
                                                        'text-halign': 'center',
                                                        'width': '200px',  # Set the node size
                                                        'height': '200px',
                                                    },
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
                                    ]
                                )
                            ], style={"display": "flex"}
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
        # Third body of the App - University Section
        html.Div(
            className="row app-body",
            children=[
                # User Controls
                html.Div(
                    className="seven columns card",
                    children=[
                        html.Div(
                            className="bg-white user-control",
                            children=[
                                html.Div(
                                    className="padding-top-bot",
                                    children=[
                                        html.H4("Search by university"),
                                        ##
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                # Fourth body of the App - Update Section
                html.Div(
                    className="five columns card",
                    children=[
                        html.Div(
                            className="bg-white5",
                            children=[
                                html.Div(
                                    className="bg-white",
                                    children=[
                                        html.H4("Found Bugs? Please update the correct data here"),
                                        html.P("You can only correct the professor information since all other dashboards are based on aggregated data."),
                                    ], style={'margin-bottom': '30px'}
                                ),
                                html.Div(
                                    #className="bg-white5 custom-background",
                                    children=[
                                        html.Div([
                                            dcc.Input(id='input-name', type='text', placeholder='Enter original name (required)', style={'width':'250px','height': '30px', 'font-size': '15px', 'display': 'inline-block', 'margin-right':'10px'}),
                                            dcc.Input(id='input-corrected-name', type='text', placeholder='Enter corrected name', style={'width':'250px','height': '30px', 'font-size': '15px', 'display': 'inline-block'}),
                                        ], style={'margin-bottom': '10px'}),
                                        html.Div([
                                            dcc.Input(id='input-position', type='text', placeholder='Enter original position', style={'width':'250px','height': '30px', 'font-size': '15px', 'display': 'inline-block', 'margin-right':'10px'}),
                                            dcc.Input(id='input-corrected-position', type='text', placeholder='Enter corrected position', style={'width':'250px','height': '30px', 'font-size': '15px', 'display': 'inline-block'}),
                                        ], style={'margin-bottom': '10px'}),
                                        html.Div([
                                            dcc.Input(id='input-email', type='text', placeholder='Enter original email', style={'width':'250px','height': '30px', 'font-size': '15px', 'display': 'inline-block', 'margin-right':'10px'}),
                                            dcc.Input(id='input-corrected-email', type='text', placeholder='Enter corrected email', style={'width':'250px','height': '30px', 'font-size': '15px', 'display': 'inline-block'}),
                                        ], style={'margin-bottom': '10px'}),
                                        html.Div([
                                            dcc.Input(id='input-phone', type='text', placeholder='Enter original phone number', style={'width':'250px','height': '30px', 'font-size': '15px', 'display': 'inline-block', 'margin-right':'10px'}),
                                            dcc.Input(id='input-corrected-phone', type='text', placeholder='Enter corrected phone number', style={'width':'250px','height': '30px', 'font-size': '15px', 'display': 'inline-block'}),
                                        ], style={'margin-bottom': '10px'}),
                                        html.Button('Submit', id='submit-button', style={'width':'300px','height': '40px', 'font-size': '15px', 'text-align': 'center'})
                                    ], style={'display': 'flex', 'flex-direction': 'column'}  
                                ),
                                # ConfirmDialog to show a pop-up when the update is successful
                                dcc.ConfirmDialog(
                                    id='revise-success-popup',
                                    message='Update successful! Now search by newly updated data',
                                ),
                                # FailDialog to show a pop-up when the update is unsuccessful
                                dcc.ConfirmDialog(
                                    id='revise-fail-popup',
                                    message='Update Failed! No matching record found for the given name and position.',
                                ),
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# Define the callback function to update the table based on the university filter input
@app.callback(
    [Output('keyword-univ-table', 'data'),
    Output('keyword-faculty-table', 'data'),
    Output('update-keyword', 'value'),
    Output('update-success-popup', 'displayed'),
    Output('update-fail-popup', 'displayed'),],
    [Input('keyword-filter', 'value'),
    Input('update-button', 'n_clicks'),],
    [State('update-keyword', 'value')]
)
def keyword_section(keyword, n_clicks, update_keyword_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    success_popup_displayed = False
    fail_popup_displayed = False

    ## First Table: keyword filter on university list
    cursor = mysqldb.cursor()
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
    cursor = mysqldb.cursor()
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
        cursor = mysqldb.cursor()
        try:
            # Get the maximum ID from the 'keyword' table
            query = "SELECT max(id) FROM keyword"
            cursor.execute(query)
            max_id = cursor.fetchall()

            # Generate the INSERT query with the new ID and name
            new_id = max_id[0][0] + 1
            query = f"INSERT INTO keyword (ID, name) VALUES({new_id}, '{update_keyword_value}')"
            cursor.execute(query)
            mysqldb.commit()
            success_popup_displayed = True

        except mysql.connector.Error as e:
            # Handle MySQL errors (e.g., check constraint violations, unique key violations)
            #mysqldb.rollback()  # Rollback the transaction to undo the changes
            fail_popup_displayed = True
        finally:
            cursor.close()
    
    return table_data1, table_data2, '', success_popup_displayed, fail_popup_displayed

@app.callback(
    Output('cytoscape-tapNodeData', 'children'),
    [Input('filter-key', 'value'),
    Input('cytoscape-network', 'mouseoverNodeData')],
)
def update_professor_graphproperty(filter_key, node_data):
    if filter_key:
        if node_data:
            property = """"""
            # Display the properties as a JSON string (customize this display as needed)
            for key, value in node_data.items():
                if not type(value) is NoneType:
                    if value != "" and value != "nan":
                        property += f"🔹 {key.capitalize()} : {value}\n"
        else:
            property = "Hover over a node to see its properties."
    else:
        property = "First select the professor and see the network graph"
    return property

@app.callback(
    [Output("key-value-textarea", "children"),
    Output("professor-img", "src"),
    Output('cytoscape-network', 'elements'),
    Output("publications-text", "children"),
    Output("summary-text", "children"),],
    [Input('filter-key', 'value'),]
)
def update_professor(filter_key):
    # professor section
    mongo_data = ""
    elements = []
    photoUrl = "assets/No-Image-Placeholder.png"

    if filter_key:
        for json_ in data_from_mongo:
            if json_['name'] == filter_key:
                photoUrl = json_['photoUrl']
                if check_image_url(photoUrl):
                    photoUrl = photoUrl
                else:
                    photoUrl = "assets/No-Image-Placeholder.png"
                for key, value in json_.items():
                    if key != 'photoUrl' and not type(value) is NoneType:
                        if value != "":
                            mongo_data += f"🔹 <b>{key.capitalize()} : </b> {value.title()}<br>"

        elements = draw_networkgraph(filter_key)

        latest_publications = fetch_google_scholar_publications(filter_key)
        summary = generate_summary_by_gpt(mongo_data, elements)
    else:
        latest_publications = ""
        summary = ""

    return mongo_data, photoUrl, elements, latest_publications, summary

@app.callback(
    [Output('revise-success-popup', 'displayed'),
    Output('revise-fail-popup', 'displayed'),],
    [Input('submit-button', 'n_clicks')],
    [State('input-name', 'value'),
     State('input-position', 'value'),
     State('input-corrected-name', 'value'),
     State('input-corrected-position', 'value'),
     State('input-phone', 'value'),
     State('input-email', 'value'),
     State('input-corrected-phone', 'value'),
     State('input-corrected-email', 'value'),]
)
def update_mongo_data(n_clicks, name, position, corrected_name, corrected_position, phone, email, corrected_phone, corrected_email):
    success_popup_displayed = False
    fail_popup_displayed = False
    if n_clicks and name and (corrected_name or corrected_position or corrected_phone or corrected_email):
        # Find the matching record based on the provided name and position
        matching_record = mongodb['faculty'].find_one({'name': name, 'position': position, 'phone':phone, 'email':email})

        if matching_record:
            update_data = {}
            if corrected_name:
                update_data['name'] = corrected_name
            if corrected_position:
                update_data['position'] = corrected_position
            if corrected_phone:
                update_data['phone'] = corrected_phone
            if corrected_email:
                update_data['email'] = corrected_email
            # Perform the update in MongoDB
            mongodb['faculty'].update_one({'_id': matching_record['_id']}, {'$set': update_data})

            # Return a confirmation message
            success_popup_displayed = True
        else:
            fail_popup_displayed = True
    return success_popup_displayed, fail_popup_displayed

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

    # Register the cleanup function with atexit
    view_lst = ['kpi_faculty','kpi_publication','kpi_university']
    atexit.register(drop_views_on_exit(view_lst))