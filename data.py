import requests
import pandas as pd
# from datetime import datetime
import constants as const
from dash.exceptions import PreventUpdate
import numpy as np
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
#     df = pd.DataFrame(json_string)
#     # 'Country' is a column as well
#     df = df[['CountryCode', 'Confirmed', 'Deaths', 'Recovered', 'Date']]
#     collection = df[df['CountryCode'] == 'IN'][[
#         'Confirmed', 'Deaths', 'Recovered', 'Date']]
    # collection = pd.MultiIndex.from_product([['IN'], collection.columns])
    # for code in df['CountryCode'].unique():
    #     if code == 'IN':
    #         continue
    #     temp = df[['Confirmed', 'Deaths', 'Recovered', 'Date']]
    #     temp.columns = pd.MultiIndex.from_product([[code], temp.columns])
    #     collection.append(temp)
    # print(collection)

    # label = label.title()
    # dailyStr = 'Daily'+label
    # df[dailyStr] = df[label] - df[label].shift()
    # # Redundancy in case calculations gives negative number
    # df[dailyStr] = df[dailyStr].apply(abs)
    # df.fillna(value=0, inplace=True)
    # print(df.memory_usage(index=True).sum())
    # # df = reduce_data(df)
    # df['DailyConfirmed'] = df['DailyConfirmed'].astype(np.int32)
    # df['DailyDeaths'] = df['DailyDeaths'].astype(np.int16)
    # df['DailyRecovered'] = df['DailyRecovered'].astype(np.int32)
    # print(df.columns)
    # print(df.memory_usage(index=True).sum())

    # df.to_csv('test.csv')
    # print(df[df['CountryCode'] == 'AF'])
    # jsondict = dict(json_string)
    # everything = jsondict.get('data')
    # print(jsondict.keys())

# if datetime.today().hour == 18:
#     get_all_data()


# def reduce_data(df):
#     df['Confirmed'] = df['Confirmed'].apply(reduce_column_size)
#     return df


# def reduce_column_size(value):
#     # if value < 128:
#     return np.int64(value)


# get_all_data()
