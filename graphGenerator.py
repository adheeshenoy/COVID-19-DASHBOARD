import constants as const
import plotly.graph_objs as go 
import ast
from datetime import datetime
import data
import pandas as pd

def tracer(graphType, dataDf):
    tracerList = None
    if graphType == const.GRAPH_TYPE.SCATTER_TOTAL_CASES:
        tracerList = __totalCases_scatter(dataDf)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_CASES:
        tracerList = __dailyCases_bar(dataDf)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_DEATHS:
        tracerList = __dailyDeaths_bar(dataDf)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_RECOVERED:
        tracerList = __dailyRecovered_bar(dataDf)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_RECOVERED_DEATHS_STACKED:
        tracerList = __dailyCasesRecoveredDeaths_Stacked_bar(dataDf)
    return tracerList

def __totalCases_scatter(dataDf):
    tracerList = []
    count = 0
    for label in const.LABELS:
        tracerList.append(go.Scatter(x =  dataDf[label]['Date'], y = dataDf[label]['Cases'],
        line = dict(color = const.COLORS[count]), name = label.title()))
        count += 1
    return tracerList 

def __dailyCases_bar(dataDf):
    tracerList = []
    if dataDf['Daily'].max() == 0:
        raise Exception('There have been no daily cases reported')
    tracerList.append(
        go.Bar(x = dataDf['Date'], y = dataDf['Daily'],
        name = 'Daily Cases', marker_color = const.COLORS[0])
    ) 
    return tracerList


def __dailyDeaths_bar(dataDf):
    tracerList = []
    if dataDf['Daily'].max() == 0:
        raise Exception('There have been no daily cases reported')
    tracerList.append(
        go.Bar(x = dataDf['Date'], y = dataDf['Daily'],
        name = 'Daily Deaths', marker_color = const.COLORS[2])
    ) 
    return tracerList

def __dailyRecovered_bar(dataDf):
    tracerList = []
    if dataDf['Daily'].max() == 0:
        raise Exception('There have been no daily cases reported')
    tracerList.append(
        go.Bar(x = dataDf['Date'], y = dataDf['Daily'],
        name = 'Daily Recovered',marker_color = const.COLORS[1])
    ) 
    return tracerList

def __dailyCasesRecoveredDeaths_Stacked_bar(dataDf):
    tracerList = []
    names = ['Daily Cases', 'Daily Recovered', 'Daily Deaths']
    for label,name,i in zip(const.LABELS, names, [0,1,2]):
        if dataDf[label]['Daily'].max() == 0:
            raise Exception('There have been no daily cases reported')
        tracerList.append(
            go.Bar(x = dataDf[label]['Date'], y = dataDf[label]['Daily'],
            name = name, marker_color = const.COLORS[i])
        ) 
    return tracerList

# LAYOUT
def layout_generator(graphType, country, showlegend):
    if graphType == const.GRAPH_TYPE.SCATTER_TOTAL_CASES:
        return __layout_generator_scatter(country, showlegend, title = 'Total Cases')
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_CASES:
        return __layout_generator_bar(country, showlegend)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_DEATHS:
        return __layout_generator_bar(country, showlegend, title = 'Daily Deaths - ')
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_RECOVERED:
        return __layout_generator_bar(country, showlegend, title = 'Daily Recovered - ')
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_RECOVERED_DEATHS_STACKED:
        return __layout_generator_bar(country, showlegend, mode= 'stack', title= ' Daily Cases and Deaths Stacked - ')
    else:
        return {}

def __layout_generator_scatter(country, showlegend, title):
    return dict(title = dict(
        text = title + ' (' + country.title() + ')',
        font = dict(
            size = 20,
            color = 'white'
            )
        ), 
        yaxis = dict(
            color = 'white',
            tickfont = dict(
                size = 16
            ),
            title = dict(
                text = 'Number of people', 
                font = dict(
                    size = 20
                )
            )
        ),
        xaxis=dict(
            color = 'white',
            tickfont = dict(
                size = 16
            ),
            showgrid = True, 
            title = dict(
                text = 'Date',
                font = dict(
                    size = 20
                )
            ),
            rangeselector=dict(
                margin = dict(
                    b = 2
                ),
                font = dict(
                    size = 14,
                    color = 'white'
                ),
                bgcolor = '#333333',
                buttons=list([
                    dict(count=1,
                        label="1 month",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(count=3,
                        label = "3 months",
                        step = "month",
                        stepmode = "backward"
                    ),
                    dict(count=6,
                        label="6 months",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(label = 'All',
                        step="all"
                    )
                ])
            )   
        ), 
        paper_bgcolor = '#222222',
        plot_bgcolor = '#222222',
        legend = dict(
            x = 0.01,
            y = 0.97,
            bgcolor = '#333333',
            font = dict(
                color = 'white',
                size = 16
            )
        )
    )

def __layout_generator_bar(country, showlegend, mode = None, title ='Daily Cases - '):
    if mode == None:
        return dict(title = dict(
        text = title + ' (' + country.title() + ')',
        font = dict(
            size = 20,
            color = 'white'
            )
        ),
        xaxis = dict(title = dict(
                text = 'Date',
                font = dict(
                    size = 20,
                    )
                ),
                color = 'white',
                tickfont = dict(
                size = 16
                ),
                showgrid = True,
                rangeselector=dict(
                    font = dict(
                    size = 14,
                    color = 'white'
                    ),
                    bgcolor = '#333333',
                    buttons=list([
                        dict(count=1,
                        label="1 month",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(count=3,
                        label = "3 months",
                        step = "month",
                        stepmode = "backward"
                    ),
                    dict(count=6,
                        label="6 months",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(label = 'All',
                        step="all"
                    )
                ]),
            ),
        ),
        yaxis = dict(title = dict(text = 'Number of cases',
                font = dict(
                    size = 20
                )
            ),
            color = 'white',
            tickfont = dict(size = 16)
            ), 
        showlegend = False,
        paper_bgcolor = '#222222',
        plot_bgcolor = '#222222'
        )
    else:
        return dict(title = dict(
            text = title + country.title(),
            font = dict(color = 'white',
                size = 20)
        ), 
        xaxis = dict(title = dict(
            text = 'Date',
            font = dict(
                size = 20
                )
            ), 
            color = 'white',
            showgrid = True, 
            tickfont = dict(size = 16),
            rangeselector=dict(
                font = dict(
                    size = 14,
                    color = 'white'
                ),
                bgcolor = '#333333',
                buttons=list([
                    dict(count=1,
                        label="1 month",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(count=3,
                        label = "3 months",
                        step = "month",
                        stepmode = "backward"
                    ),
                    dict(count=6,
                        label="6 months",
                        step="month",
                        stepmode="backward"
                    ),
                    dict(label = 'All',
                        step="all"
                    )
                ])
            ) 
        ),
        yaxis = dict(title = dict(
            text = 'Number of cases',
            font = dict(
                size = 20
            )
        )
        , color = 'white', tickfont = dict(size = 16)), showlegend = True, barmode = mode,
        paper_bgcolor = '#222222', plot_bgcolor = '#222222', legend = dict(
            x = 0.01,
            y = 0.95,
            bgcolor = '#333333',
            font = dict(
                color = 'white',
                size = 16
            )
        ))


def __continent_map(df):
    return go.Choropleth(locations = df['CountryCode'].apply(lambda iso2: const.ISO2_TO_ISO3.get(str(iso2))),
    z = df['TotalConfirmed'],text = df['Country'],colorscale = 'twilight',autocolorscale=False,
    reversescale=True,colorbar = dict(len = 0.5, tickcolor = 'white', tickfont = dict(size = 16, color  = 'white'))) 

def __layout_generator_map(country):
    return dict(title = dict(
        text = 'Continent Overview Total Cases',
        font = dict(color = 'white',
                    size = 20)
        ),
                height= 1000,
                geo=dict(
                    scope = const.CONTINENTS.get(const.ISO2_CONTINENT.get(const.COUNTRYISO2.get(country))),
                    showframe= True,
                    showcoastlines=False,
                    projection_type='equirectangular',
                    bgcolor = 'rgba(34,34,34,34)',
                    countrycolor = 'white',
                    countrywidth = 1.5,
                ),
                dragmode = False,
                paper_bgcolor = '#222222'
            )

def get_map(country, summaryDf):
    return dict(data = [__continent_map(summaryDf)], layout = __layout_generator_map(country))  
