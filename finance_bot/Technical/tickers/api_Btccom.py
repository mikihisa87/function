from datetime import datetime, timezone, timedelta
import pandas as pd
import requests

def get_from_api():
    btc_info = requests.get("https://chain.api.btc.com/v3/block/latest").json()
    return btc_info

def get_time(latest_data):
    time = latest_data['data']['curr_max_timestamp']
    time = datetime.fromtimestamp(time, timezone.utc)
    return time

def get_height(latest_data):
    height = latest_data["data"]["height"]
    return height

def get_difficulty(latest_data):
    difficulty = latest_data["data"]["difficulty"]
    return difficulty

def get_size(latest_data):
    size_byte = latest_data['data']["size"]
    return size_byte

def get_hashrate(latest_data):
    diff = get_difficulty(latest_data)
    hashrate = (diff * 2**32 / 600) / 1000000000000000000
    return hashrate
    
def ticker():
    latest_data = get_from_api()
    time = get_time(latest_data)
    height = get_height(latest_data)
    difficulty = get_difficulty(latest_data)
    size_byte = get_size(latest_data)
    hashrate = get_hashrate(latest_data)
    
    return time, height, difficulty, size_byte, hashrate