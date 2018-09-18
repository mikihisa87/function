import requests
import sys, os
sys.path.append(os.pardir)
from datetime import datetime, timezone, timedelta
import api_poloniex as api
from pandas_highcharts.display import display_charts
from ipywidgets import interact
import alto_data
import numpy as np
import csv
import api_poloniex as api

def settle(currency, period):
    currency = currency
    period = period
    start = datetime(2017,12,1,0,0,0).strftime("%s") 
    end = datetime(2017,12,29,0,0,0).strftime("%s")
    url = api.select(currency, api.unix(start), api.unix(end), period)
    try:
        get = api.get_currency(url)
        path = "../alto_data/"
        get.to_csv(path + "{}.csv".format(currency))
    except:
        print("Please select pull-down menu")
    
interact(settle, currency=["", "ETH","XRP","DOGE","LTC","STR","XMR","BTS","DASH","MAID","FCT","CLAM"],
         period=["", "300", "900", "1800", "7200", "14400", "86400"]);