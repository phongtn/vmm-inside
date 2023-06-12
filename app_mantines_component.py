from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px 
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Incoporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app - incorporate css
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# In this version we use Dash Mantine Components to stylesheet. Ref: https://www.dash-mantine-components.com/components/button
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dmc.Container([
        dmc.Title('My First App with Data, Graph, and Controls', color="blue", size="h3"),

        dmc.RadioGroup(
                        [dmc.Radio(i, value=i) for i in ['pop', 'lifeExp', 'gdpPercap']],
                        value='lifeExp',
                        size="sm", 
                        id='my-dmc-radio-item'),
        
        dmc.Grid([
            dmc.Col([
                dash_table.DataTable(data=df.to_dict('records'), page_size=12, style_table={'overflowX':'auto'})
            ], span=5),
            dmc.Col([
                dcc.Graph(figure={}, id='graph-placeholder')
            ], span=5),
            dmc.Col([
                dmc.Button("Settings", variant="outline", leftIcon=DashIconify(icon="fluent:settings-32-regular"))
            ], span=2),
        ]),
    ], fluid=True)

# Add controls to build the interaction
@callback(
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='my-dmc-radio-item', component_property='value')
)

def update_graph(col_chosen):
    return px.histogram(df, x='continent', y=col_chosen, histfunc='avg')

# Run the dashboard
if __name__ == '__main__':
    app.run_server(debug=True)

