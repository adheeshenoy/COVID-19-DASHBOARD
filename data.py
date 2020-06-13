import requests
import pandas as pd
from datetime import datetime
import constants as const
from dash.exceptions import PreventUpdate
# import json
# import ast


def get_summary():
    url = 'https://api.covid19api.com/summary'
    json_string = requests.get(url).json()
    df = pd.DataFrame(json_string['Countries'])
    return df[['Country', 'CountryCode', 'Slug', 'TotalConfirmed', 'TotalDeaths', 'TotalRecovered']].to_json()


def get_total_daily_df(country, label):
    url = 'https://api.covid19api.com/total/dayone/country/{country}/status/{label}'.format(
        country=country, label=label)
    json_string = requests.get(url).json()
    df = pd.DataFrame(json_string)
    try:
        df = df[['Cases', 'Date']]
        df['Daily'] = df['Cases'] - df['Cases'].shift()
        df['Daily'] = df['Daily'].apply(abs)
        df.fillna(value=0, inplace=True)
        return df
    except:
        raise Exception('Df cannot be parsed')


def get_data(country):
    data_dict = {}
    for label in const.LABELS:
        data_dict[label] = get_total_daily_df(country, label)
    return data_dict['confirmed'].to_json(), data_dict['recovered'].to_json(),\
        data_dict['deaths'].to_json()


# def get_all_data():
#     url = 'https://api.covid19api.com/all'
#     json_string = requests.get(url).json()
    # jsondict = dict(json_string)
    # everything = jsondict.get('data')
    # print(jsondict.keys())
    # df = pd.DataFrame(json_string)
    # df = df[['Country', 'CountryCode', 'Confirmed', 'Deaths', 'Recovered', 'Date']]
    # df.to_csv('test.csv')
    # print(df.memory_usage(index=True).sum())
    # df['DailyConfirmed'] = df['Confirmed'] - df['Confirmed'].shift()
    #     df['Daily'] = df['Daily'].apply(abs)
    #     df.fillna(value=0, inplace=True)
    # print(df[df['CountryCode'] == 'AF'])


# if datetime.today().hour == 18:
#     get_all_data()
