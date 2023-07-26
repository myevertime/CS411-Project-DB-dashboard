# Import required libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("University Explorer: Find Your Best-fit ML/AI University"),
    
    dcc.Graph(
        id='simple-graph',
        figure={
            'data': [
                {'x': [1, 2, 3, 4, 5], 'y': [3, 1, 4, 6, 2], 'type': 'bar', 'name': 'Category 1'},
                {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 1, 5, 3], 'type': 'bar', 'name': 'Category 2'},
            ],
            'layout': {
                'title': 'Simple Bar Chart',
                'xaxis': {'title': 'X-axis'},
                'yaxis': {'title': 'Y-axis'},
            }
        }
    ),
    
    dcc.Slider(
        id='slider-input',
        min=0,
        max=10,
        step=1,
        value=5,
        marks={i: str(i) for i in range(11)}
    ),
    
    html.Div(id='slider-output')
])

# Define the callback function to update the output based on the slider input
@app.callback(
    Output('slider-output', 'children'),
    [Input('slider-input', 'value')]
)
def update_output(value):
    return f'The selected value is {value}'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
