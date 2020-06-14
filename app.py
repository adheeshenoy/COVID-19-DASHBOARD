import dash
import dash_core_components as dcc
import dash_html_components as html 
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import constants as const
import data
import ast
import pandas as pd
import plotly.graph_objs as go
import graphGenerator as gg
from datetime import datetime
import numpy as np

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

server = app.server

# Navigation 
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Countries", href="#")),
        dbc.NavItem(dbc.NavLink('WorldWide',href = '#'))
    ],
    brand="COVID-19 Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
    fluid = True,
    brand_style = dict(fontSize = 30)
)

country_dropdown = dcc.Dropdown(
        id = 'country-dropdown',
        options = const.COUNTRY_DROPDOWN,
        value = 'united-states',
        clearable = False
    )

graph_dropdown = dcc.Dropdown(
        id = 'graphs-dropdown',
        options = const.GRAPH_DROPDOWN,
        value = const.GRAPH_TYPE.SCATTER_TOTAL_CASES,
        clearable = False
    )


summary_tab = dbc.Card(
    dbc.CardBody([   
            html.H3('Total Cases',id = 'total-cases'),
            html.H3('Total Deaths',id = 'total-deaths'),
            html.H3('Total Recovered',id = 'total-recovered'),
            html.H3('Recovery Rate', id = 'recovery-rate'),
            html.H3('Death Rate', id = 'death-rate')
        ]
        #  'height':'26rem'
    ), style = {'text-align':'center', 'background': const.PRIMARY_HEX}, color = 'white', outline = True
)

overview_tab = dbc.Card(
    dbc.CardBody([
            dcc.DatePickerSingle(
                id = 'overview-date-picker',
                initial_visible_month = datetime.now(),
                placeholder = 'Select Date',
                display_format='MMM Do, YY',
                style = dict(padding = 10)
            ),
            html.H3('Daily Cases: ',id = 'daily-cases'),
            html.H3('Daily Recovered: ',id = 'daily-recovered'),
            html.H3('Daily Deaths: ',id = 'daily-deaths')
        ]
        # 'height':'26rem'
    ), style = {'text-align':'center', 'background': const.PRIMARY_HEX}, color = 'white', outline = True
)

stat_selector = dbc.Tabs(
    [
        dbc.Tab(summary_tab, label="Summary", tab_style = {'margin-top':'1rem', 'cursor':'pointer', 'background': const.PRIMARY_RGB}, label_style = {'font-size': '20px'}),
        dbc.Tab(overview_tab, label="Overview", tab_style = {'margin-top':'1rem', 'cursor':'pointer', 'background': const.PRIMARY_RGB},label_style = {'font-size': '20px'}),
    ],id = 'statSelector', className = 'nav-justified'
)

app.layout = html.Div([
    html.Div([
        dcc.Store(id='confirmed-data', storage_type='local'),
        dcc.Store(id='recovered-data', storage_type='local'),
        dcc.Store(id='deaths-data', storage_type='local'),
        dcc.Store(id='world-data', storage_type = 'local', data = data.get_summary()),
        dcc.Store(id='current-country-data', storage_type = 'local')
    ], id = 'local-storage'),
    html.Div([
        navbar
    ], id ='banner'),
    html.Div([
        dbc.Alert(
            "The website was put in landscape for better visualization.",
            id="warning",
            dismissable=True,
            fade=True,
            color = 'warning',
        ),
        country_dropdown,
        graph_dropdown,
        dbc.Alert(
            "Unavailable to perform country! Showing previous country information",
            id="alert",
            dismissable=True,
            fade=True,
            is_open= False,
            color = 'danger',
            duration = 2000
        )
    ], id = 'dropdowns'),
    html.Div([
        dcc.Graph(id = 'main-graph', config = dict(displaylogo = False), figure = go.Figure(data = [],layout = dict(paper_bgcolor = '#222222',plot_bgcolor = '#222222', xaxis = dict(visible = False),yaxis = dict(visible = False))))
    ], className = 'graph'),
    html.Div(
        stat_selector
            ),
    html.Div([
        dcc.Graph(id = 'map', className = 'country',config = dict(scrollZoom = False, displaylogo = False, displayModeBar = False))
    ], className = 'mapify')
])

@app.callback(
    Output('map','figure'),
    [Input('confirmed-data', 'data'),
    Input('world-data','data'),
    Input('current-country-data', 'data')]
)
def create_map(confirmed, summary, country):
    if confirmed:
        summary = string_to_df(summary)
        return gg.get_map(country,summary)
    else:
        raise PreventUpdate

@app.callback(
    [Output('total-cases', 'children'),
    Output('total-deaths', 'children'),
    Output('total-recovered', 'children'),
    Output('recovery-rate', 'children'),
    Output('death-rate', 'children')],
    [Input('world-data','data'),
    Input('current-country-data', 'data')]
)
def update_summary(summary, country):
    try:
        summary = string_to_df(summary)
        totalConfirmed = int(summary[summary['Slug'] == country]['TotalConfirmed'])
        totalDeaths = int(summary[summary['Slug'] == country]['TotalDeaths'])
        totalRecovered = int(summary[summary['Slug'] == country]['TotalRecovered'])
        return 'Total Confirmed: {:,}'.format(totalConfirmed),\
            'Total Deaths: {:,}'.format(totalDeaths),\
            'Total Recovered: {:,}'.format(totalRecovered),\
            'Recovery Rate: {:.2%}'.format(totalRecovered/totalConfirmed),\
            'Death Rate: {:.2%}'.format(totalDeaths/totalConfirmed)
    except Exception as e:
        print('Update summary: ',e)
        raise PreventUpdate

@app.callback(
    [Output('daily-cases', 'children'),
    Output('daily-recovered','children'),
    Output('daily-deaths','children'),
    Output('overview-date-picker','min_date_allowed'),
    Output('overview-date-picker','max_date_allowed')],
    [Input('overview-date-picker', 'date'),
    Input('confirmed-data','data'),
    Input('recovered-data','data'),
    Input('deaths-data','data')]
)
def update_overview(date, confirmed, recovered, deaths):
    try:
        confirmed = string_to_df(confirmed)
        recovered = string_to_df(recovered)
        deaths = string_to_df(deaths)
        maxDate = confirmed['Date'].max()
        minDate = confirmed['Date'].min()
        if date != None:
            date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%SZ')
            dailyCases = int(confirmed[confirmed['Date']==date]['Daily'])
            dailyRecovered = int(recovered[recovered['Date']==date]['Daily'])
            dailyDeaths = int(deaths[deaths['Date']==date]['Daily'])
            return 'Daily Cases: {:,}'.format(dailyCases),\
                'Daily Recovered: {:,}'.format(dailyRecovered),\
                'Daily Deaths: {:,}'.format(dailyDeaths),\
                minDate,maxDate
        else:
            return 'Daily Cases: ','Daily Recovered','Daily Deaths: ', minDate, maxDate
    except Exception as e:
        print('Update overview: ', e)
        raise PreventUpdate
        

def string_to_df(string):
    '''Helper function that returns the dataframe from a string'''
    if isinstance(string, str):
        return pd.DataFrame(ast.literal_eval(string))


# Data updating and storing
@app.callback(
    [Output('confirmed-data','data'),
    Output('recovered-data','data'),
    Output('deaths-data','data'), 
    Output('current-country-data','data')],
    [Input('country-dropdown', 'value')]
)
def update_data(country):
    try:
        confirmed,recovered,deaths = data.get_data(country)
        return confirmed, recovered, deaths, country
    except:
        # return '','',''
        raise PreventUpdate

# Graph plotting
@app.callback(
    Output('main-graph', 'figure'),
    [Input('confirmed-data', 'data'),
    Input('recovered-data','data'),
    Input('deaths-data','data'),
    Input('graphs-dropdown','value'),
    Input('current-country-data', 'data')]
)
def update_graph(confirmed, recovered, deaths, graphType, country):
    try:
        confirmed = string_to_df(confirmed)
        recovered = string_to_df(recovered)
        deaths = string_to_df(deaths)
        current_figure = None
        if graphType == const.GRAPH_TYPE.SCATTER_TOTAL_CASES:
            data = {'confirmed':confirmed,'recovered':recovered,'deaths':deaths}
            current_figure = dict(data = gg.tracer(const.GRAPH_TYPE.SCATTER_TOTAL_CASES,data),
            layout = gg.layout_generator(const.GRAPH_TYPE.SCATTER_TOTAL_CASES,country, True))
        elif graphType == const.GRAPH_TYPE.BAR_DAILY_CASES:
            current_figure = dict(data = gg.tracer(const.GRAPH_TYPE.BAR_DAILY_CASES, confirmed),
            layout = gg.layout_generator(const.GRAPH_TYPE.BAR_DAILY_CASES,country, True))
        elif graphType == const.GRAPH_TYPE.BAR_DAILY_DEATHS:
            current_figure = dict(data = gg.tracer(const.GRAPH_TYPE.BAR_DAILY_DEATHS, deaths),
            layout = gg.layout_generator(const.GRAPH_TYPE.BAR_DAILY_DEATHS,country, True)) 
        elif graphType == const.GRAPH_TYPE.BAR_DAILY_RECOVERED:
            current_figure = dict(data = gg.tracer(const.GRAPH_TYPE.BAR_DAILY_RECOVERED, recovered),
            layout = gg.layout_generator(const.GRAPH_TYPE.BAR_DAILY_RECOVERED,country, True)) 
        elif graphType == const.GRAPH_TYPE.BAR_DAILY_RECOVERED_DEATHS_STACKED:
            data = {'confirmed':confirmed, 'recovered':recovered,'deaths': deaths}
            current_figure = dict(data = gg.tracer(const.GRAPH_TYPE.BAR_DAILY_RECOVERED_DEATHS_STACKED,data),
            layout = gg.layout_generator(const.GRAPH_TYPE.BAR_DAILY_RECOVERED_DEATHS_STACKED,country, True))
        return current_figure
    except Exception as e:
        print('Update Graph: ', e)
        raise PreventUpdate

@app.callback(
    [Output('alert', 'is_open'),
    Output('alert','children')],
    [Input('country-dropdown','value'),
    Input('current-country-data', 'data')]
)
def toggle_alert(country, currentCountry):
    if country != currentCountry:
        return True, const.WARNING_MESSAGE.format(country = country.title())
    else:
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug = True)