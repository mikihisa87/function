from api_Btccom import ticker
from block_tickers import insert

def main():
    try_count = 5
    ticks = None
    while ticks is None and try_count > 0:
        try:
            ticks = ticker()
        except Exception as e:
            print('If Exception occured, try again.')
            try_count -= 1
    insert({"time": ticks[0], "height": ticks[1], "difficulty": ticks[2], "size_byte": ticks[3], "hashrate": ticks[4]})

if __name__ == '__main__':
    main()