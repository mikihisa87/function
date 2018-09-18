from datetime import datetime, timezone, timedelta
import requests
import multiprocessing

def fetch(url):
    return requests.get(url).json()
    
def get_from_api():
    urls = [
        "https://chain.so/api/v2/get_info/BTC",
        "https://bitaps.com/api/block/latest",
        "https://etherchain.org/api/blocks/0:offset/1:count",
        "https://api.nanopool.org/v1/eth/network/lastblocknumber",
        "https://api.nanopool.org/v1/eth/pool/hashrate",
        "https://api.nanopool.org/v1/eth/pool/activeminers"
    ]
    q = multiprocessing.Pool(len(urls))
    result = q.map(fetch, urls)
    q.close()
    return result

def get_time(latest_bitaps, latest_etherchain):
    bitaps_time = latest_bitaps['timestamp']
    bitaps_time = datetime.fromtimestamp(bitaps_time, timezone.utc)
    eth_time = latest_etherchain['data'][0]['time']
    return bitaps_time, eth_time

def get_height(latest_chain, latest_bitaps, latest_etherchain, latest_ethbk):
    chian_height = latest_chain['data']['blocks']
    bitaps_height = latest_bitaps['height']
    eth_height = latest_etherchain['data'][0]['number']
    eth_hg_nan = latest_ethbk['data']
    return chian_height, bitaps_height, eth_height, eth_hg_nan

def get_hashrate(latest_chain, latest_ethhash):
    chain_hash = latest_chain['data']['hashrate']
    eth_hash = latest_ethhash['data']
    return chain_hash, eth_hash

def get_diff(latest_chain, latest_etherchain):
    chain_diff = latest_chain['data']['mining_difficulty']
    eth_diff = latest_etherchain['data'][0]['difficulty']
    return chain_diff, eth_diff

def get_txs(latest_bitaps, latest_etherchain):
    bitaps_txs = latest_bitaps['transactions']
    eth_txs = latest_etherchain['data'][0]['tx_count']
    return bitaps_txs, eth_txs

def get_miner(latest_ethmin):
    eth_miner = latest_ethmin['data']
    return eth_miner
    
def ticker():
    latest_data = get_from_api()
    latest_chain = latest_data[0]
    latest_bitaps = latest_data[1]
    latest_etherchain = latest_data[2]
    latest_ethbk = latest_data[3]
    latest_ethhash = latest_data[4]
    latest_ethmin = latest_data[5]
    
    height = get_height(latest_chain, latest_bitaps, latest_etherchain, latest_ethbk)
    chain_height = height[0]
    bitaps_height = height[1]
    eth_height = height[2]
    eth_hg_nan = height[3]
    hash_ = get_hashrate(latest_chain, latest_ethhash)
    chain_hash = hash_[0]
    eth_hash = hash_[1]
    diff = get_diff(latest_chain, latest_etherchain)
    chain_diff = diff[0]
    eth_diff = diff[1]
    time = get_time(latest_bitaps, latest_etherchain)
    bitaps_time = time[0]
    eth_time = time[1]
    txs = get_txs(latest_bitaps, latest_etherchain)
    bitaps_txs = txs[0]
    eth_txs = txs[1]
    eth_miner = get_miner(latest_ethmin)
        
    tickers_ = {'btc_time': bitaps_time, 'btc_hgt': chain_height, 'btc_hashrate': chain_hash, 'btc_diff': chain_diff,              'btc_hgt_bp': bitaps_height,'btc_txs_bp': bitaps_txs, 'eth_time': eth_time, 'eth_hgt': eth_height,              'eth_diff': eth_diff,'eth_txs': eth_txs, 'eth_hgt_pl': eth_hg_nan,              'eth_hash_pl': eth_hash, 'eth_miner_pl': eth_miner}
    
    return tickers_

hold = ticker()

print("btc_time : " + str(hold[0])) # 0
print("btc_height : " + str(hold[1])) # 1
print("btc_hash : " + str(hold[2])) # 2
print("btc_diff : " + str(hold[3])) # 3
print("btc_height_bp : " + str(hold[4])) # 4
print("btc_txs_bp : " + str(hold[5])) # 5
print("eth_time : " + str(hold[6])) # 6
print("eth_height : " + str(hold[7])) # 7
print("eth_diff : " + str(hold[9])) # 8
print("eth_txs : " + str(hold[8])) # 9
print("eth_hgt_pl : " + str(hold[10])) # 10
print("eth_hash_pl : " + str(hold[11])) # 11
print("eth_miner_pl : " + str(hold[12])) # 12