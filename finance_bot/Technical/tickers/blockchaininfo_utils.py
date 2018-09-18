from blockchain import statistics
from datetime import datetime, timezone, timedelta
import pandas as pd

def get_from_api():
    transaction = statistics.get_chart("transactions-per-second", time_span="2minutes", api_code="")
    ts_value = transaction.values
    return ts_value
    
def get_transaction_time(latest_data):
    min_tm = latest_data
    min_tm = min_tm[0]
    min_tm = min_tm.x
    utc = datetime.fromtimestamp(min_tm, timezone.utc) # UTC
    return utc

def get_transactions(latest_data):
    min_ts = latest_data
    min_ts = min_ts[0]
    num_ts = min_ts.y * 60 # rate/s * 60
    return num_ts

def ticker():
    latest_data = get_from_api()
    transaction_time = get_transaction_time(latest_data)
    transactions = get_transactions(latest_data)
    return transaction_time, transactions