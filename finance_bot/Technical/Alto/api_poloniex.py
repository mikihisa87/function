import requests
from datetime import datetime, timezone, timedelta
import time
import pandas as pd
import csv
import os
from ipywidgets import interact

def unix(time):
    time = str(int(time) + 32400)
    return time

def select(currency, start, end, period):
    base1 = "https://poloniex.com/public?command=returnChartData&currencyPair=BTC_"
    base2 = "&start="
    base3 = "&end="
    base4 = "&period="
    url = base1+currency+base2+start+base3+end+base4+period
    return url

def get_currency(url):
    contents = requests.get(url)
    content = contents.json()
    table = []
    for i in range(len(content)):
        #info = content[i]
        Time = content[i]["date"]
        Time = datetime.utcfromtimestamp(Time)
        High = content[i]["high"]
        Low = content[i]["low"]
        Open = content[i]["open"]
        Close = content[i]["close"]
        Volume = content[i]["volume"]
        add = Time,High,Low,Open,Close,Volume
        table.append(add)
    table = pd.DataFrame(table)
    table.rename(columns={0:"Time", 1:"High", 2:"Low", 3:"Open", 4:"Close",                          5:"Volume"}, inplace=True)
    table.set_index("Time", inplace=True)
    return table
                        
def dollers(currency, start, end, period):
    base1 = "https://poloniex.com/public?command=returnChartData&currencyPair="
    base2 = "_BTC&start="
    base3 = "&end="
    base4 = "&period="
    url = base1+currency+base2+start+base3+end+base4+period
    return url

def get_usd(url):
    contents = requests.get(url)
    content = contents.json()
    table = []
    for i in range(len(content)):
        info = content[i]
        Time = content[i]["date"]
        Time = datetime.utcfromtimestamp(Time)
        High = content[i]["high"]
        Low = content[i]["low"]
        Open = content[i]["open"]
        Close = content[i]["close"]
        Volume = content[i]["volume"]
        add = Time,High,Low,Open,Close,Volume
        table.append(add)
    table = pd.DataFrame(table)
    table.rename(columns={0:"us_Time", 1:"us_High", 2:"us_Low", 3:"us_Open", 4:"us_Close",                          5:"us_Volume"}, inplace=True)
    table.set_index("us_Time", inplace=True)
    return table