from lib import bitflyer_fx as fx
import requests
from retry import retry 
import logging
import logging.config

import numpy as np
import time
import timeit
import gc
import objgraph
import pprint
import json, sys
from retry import retry

Time = 3
@retry(delay=Time, logger=logging)
def bitflyerFX():
    try:
        price = fx.Return()
        price = int(price[0]),int(price[1])
    except:
        print("Error bitflyerFX")
    return price

@retry(delay=Time, logger=logging)
def bitflyer():
    try:
        URL = "https://lightning.bitflyer.jp/v1/getticker"
        ticker = requests.get(URL).json()
        price = int(ticker["best_ask"]),int(ticker["best_bid"])
    except:
        print("Error bitflyer")
    return price

@retry(delay=Time, logger=logging)
def coincheck():
    try:
        URL = 'https://coincheck.com/api/ticker'
        ticker = requests.get(URL).json() 
        price = int(ticker['ask']),int(ticker['bid'])
    except:
        print("Error coincheck")
    return price

@retry(delay=Time, logger=logging)
def zaif():
    try:
        url = 'https://api.zaif.jp/api/1/ticker/btc_jpy'
        ticker = requests.get(url).json()
        price = int(ticker['ask']),int(ticker['bid'])
    except:
        print("Error zaif")
    return price
    
@retry(delay=Time, logger=logging)
def btcbox():
    try:
        url = 'https://www.btcbox.co.jp/api/v1/ticker'
        ticker = requests.get(url).json()
        price = int(ticker['sell']),int(ticker['buy']) # Sell 売気配 Buy 買気配
    except:
        print("Error btcbox")
    return price

@retry(delay=Time, logger=logging)
def bitbank():
    try:
        URL = 'https://public.bitbank.cc/btc_jpy/ticker'
        ticker = requests.get(URL).json()['data']
        price = int(ticker['sell']),int(ticker['buy'])
    except:
        print("Error bitbank")
    return price

@retry(delay=Time, logger=logging)
def kraken():
    try:
        url = 'https://api.kraken.com/0/public/Ticker?pair=XXBTZJPY'
        ticker = requests.get(url).json()['result']['XXBTZJPY']
        price = int(float(ticker['a'][0])),int(float(ticker['b'][0]))
    except:
        print("Error kraken")
    return price

@retry(delay=Time, logger=logging)
def quoinex():
    try:
        url = 'https://api.quoine.com/products/5'
        ticker = requests.get(url).json()
        price = int(ticker['market_ask']),int(ticker['market_bid'])
    except:
        print("Error quoinex")
    return price

@retry(delay=Time, logger=logging)
def fisco():
    try:
        url = 'https://api.fcce.jp/api/1/ticker/btc_jpy'
        ticker = requests.get(url).json()
        price = int(ticker['ask']),int(ticker['bid'])
    except:
        print("Error fisco")
    return price

bet = 400000
fine = 0.0004
bitflyerFX_swap = 0.0004
cc_long = 0.0004
cc_short = 0.0005
bitbox_swap = 0.001
quoinex_swap = 0.0005
Swap = "_swap"
oneday = 86400
TimeLeft = oneday - 1800 # 23時間半
ma_n = 20 # 移動平均期間
std_n = 5 # 標準偏差の値

def main():
    transaction = 0
    trans_time = 0 # EntryからExitまでの時間 
    trans_cnt = 0 # EntryからExitまでの回数
    hold = []
    hold_times = 0 # hold回数格納
    profit = 0
    while True:
        x = [coincheck(),btcbox(),quoinex()]
        store = ['coincheck','btcbox','quoinex']
        #x = [btcbox(),quoinex()]
        #store = ['btcbox','quoinex']
        
        def exchanges(x, store):
            ask, bid = [], []
            for i in x:
                ask.append(i[0])
                bid.append(i[1])

            ask_dic = {}
            bid_dic = {}
            count = 0
            for i in store:
                ask_dic.update({ask[count]:i})
                bid_dic.update({bid[count]:i})
                count +=1
            best_ask = sorted(ask)[0]
            best_bid = sorted(bid)[-1]
            exch_ask = ask_dic[best_ask] # 買い（最安値）の取引所を格納
            exch_bid = bid_dic[best_bid] # 売る（最高値）の取引所を格納
            ask_dict = {v:k for k,v in ask_dic.items()}
            bid_dict = {v:k for k,v in bid_dic.items()}
            Bbid_ask = ask_dict[exch_bid]
            Bask_bid = bid_dict[exch_ask]
            
            if exch_ask == exch_bid: # best_ask >= best_bid
                print("No match condition... Retry")
                time.sleep(10)
                exchanges(x, store)
            else:
                pass    
            return exch_ask, best_ask, exch_bid, best_bid, Bbid_ask, Bask_bid
        exch_info = exchanges(x, store)
        exch_ask = exch_info[0]
        best_ask = exch_info[1]
        exch_bid = exch_info[2]       
        best_bid = exch_info[3]
        Bbid_ask = exch_info[4]
        Bask_bid = exch_info[5]

        diff_price = best_bid - best_ask
        #diff_price2 = Bbid_ask - best_ask
        ratio = round((1-(best_ask/best_bid))*100,3) # 値差の比率
        msg = exch_ask+" Ask "+str(best_ask)+" "+exch_bid+" Bid "+str(best_bid)+" DiffPrice "\
        +str(diff_price)+" DiffRate "+str(ratio)+"%"        
        #logger.info(msg)
        print(msg)

        # tracking用価格差の移動平均
        def std():
            if hold_times > ma_n:
                print("---システム稼働中---\n")
                hold.append(diff_price)
                hold.pop(0)
                ma_price = int(sum(hold[:-1])/ma_n)
                ma_array = np.array(hold[:-1])
                std_ = np.std(ma_array)*std_n
                std_plus = int(ma_price+std_)
                std_min = int(ma_price-std_)
                std_between = std_plus - std_min
            else:
                hold.append(diff_price)
                std_plus = diff_price
                std_min = diff_price
                std_between = 0
                ma_price = 0
            return std_plus, std_min, std_between, ma_price

        std_price = std()
        std_plus = std_price[0]
        std_min = std_price[1]
        std_between = std_price[2]
        ma_price = std_price[3]
        print("STD_Plus",std_plus)
        print("STD_Min",std_min)
        print("STD_Between ",std_between,"MA_Price",ma_price,"入力価格",diff_price)
        print(hold,"\n")
        
        # Entry時の利益
        def first_pl(SellPrice, BuyPrice):
            fp = SellPrice - BuyPrice
            return fp
        
        # tracking different ratio
        def difference(track_bid, track_ask, track_BPrice, track_APrice, track_maxB, track_minA):
            track_diff = round((1-(track_bid/track_ask))*100,3)
            track_diffPrice = round(track_BPrice-track_APrice,0)
            track_diffAll = track_maxB - track_minA
            return track_diff, track_diffPrice, track_diffAll
        
        # 利益予測
        def pl_predict(entry_APrice, track_APrice, entry_BPrice, track_BPrice, track_diff,  track_diffPrice, ratio, diff_price):
            ask_pl = (-entry_APrice*(1+fine)) + (track_APrice*(1-fine))
            bid_pl = (entry_BPrice*(1-fine)) - (track_BPrice*(1+fine))
            PricePL = int(ask_pl+bid_pl)
            diff_ratio = round(track_diff/ratio,3)
            diff_cost = round(PricePL/diff_price,3)
            track_info = "予想収益 "+str(PricePL)+" 価格差 "+str(track_diffPrice)+" 価格差レート "+str(track_diff)+\
            " 収束レート(率) "+str(diff_ratio)+" 収束レート(価格差) "+str(diff_cost)+"\n"
            print(track_info)
            return PricePL, diff_ratio, diff_cost
        
        # 結果出力
        timer = 0 # 強制決済用タイマー
        def result(PricePL, diff_ratio, diff_cost, timer, trans_time, profit, transaction):
            print("---------------------------------------------------------")
            pl_info = "|利確| "+str(PricePL)+" 収束レート(率) "+str(diff_ratio)+\
                        "%"+" 収束レート(価格差) "+str(diff_cost)
            print(pl_info)
            print("---------------------------------------------------------")
            #logger.info(pl_info)
            return
                
        # Entry条件
        if diff_price > std_plus:
            print("!!!Follower arbitrage!!!\n")

            def entry_askL(): # 最安値取引所のask価格でLong
                entry_vol = round(bet/best_ask,8) # bet金額での初回購入量
                if exch_ask == "coincheck": 
                    entry_price = int(bet*(1+cc_long))
                else:
                    entry_price = bet # 初回BTCの販売金額
                return entry_vol, entry_price
            entry_info = entry_askL()
            entry_vol = entry_info[0]
            entry_ALPrice = entry_info[1]
            print("Entry購入数量 "+str(entry_vol)+" 購入金額 "+str(entry_ALPrice))

            def entry_bidS():
                if exch_bid == "coincheck": 
                    entry_price = int(best_bid*entry_vol*(1-cc_short))
                else:
                    entry_price = int(best_bid*entry_vol) # 初回BTCの販売金額
                return entry_price
            entry_BSPrice = entry_bidS()
            print("Entry売却数量 "+str(entry_vol)+" 売却金額 "+str(entry_BSPrice))
            
            fp = first_pl(entry_BSPrice, entry_ALPrice)
            print("Entry値差 " + str(fp) +"\n")
            
            while True:
                # 最安値取引所のbid価格(売却予定)をtracking
                def track_askL(): 
                    track_askL = eval(exch_ask)()
                    track_Lask = track_askL[0]
                    track_Lbid = track_askL[1]
                    track_ALPrice = int(entry_vol * track_Lbid)
                    return exch_ask, track_Lask, track_Lbid, track_ALPrice  
                track_askLInfo = track_askL()
                exch_ask = track_askLInfo[0]
                track_Lask = track_askLInfo[1]
                track_Lbid = track_askLInfo[2]
                track_ALPrice = track_askLInfo[3]
                print(exch_ask+" Tarcking 売却予定金額 "+str(track_ALPrice))
                
                # 最高値取引所のask価格(購入予定)をtracking
                def track_bidS():
                    track_bidS = eval(exch_bid)()
                    track_Sask = track_bidS[0]
                    track_Sbid = track_bidS[1]
                    track_BSPrice = int(entry_vol * track_Sask)
                    return exch_bid, track_Sask, track_Sbid, track_BSPrice
                track_bidSInfo = track_bidS()
                exch_bid = track_bidSInfo[0]
                track_Sask = track_bidSInfo[1]
                track_Sbid = track_bidSInfo[2]
                track_BSPrice = track_bidSInfo[3]
                print(exch_bid+" Tarcking 購入予定金額 "+str(track_BSPrice))
                
                # tracking different ratio
                diff_info = difference(track_Lbid, track_Sask, track_ALPrice, track_BSPrice, track_Sbid, track_Lask)
                track_diff = diff_info[0]
                track_diffPrice = diff_info[1] 
                track_diffAll = diff_info[2]
                print("取引所間値差",track_diffAll)
                
                # 利益予測
                track_info = pl_predict(entry_ALPrice, track_ALPrice, entry_BSPrice, track_BSPrice,\
                                        track_diff, track_diffPrice, ratio, diff_price)
                PricePL = track_info[0]
                diff_ratio = track_info[1]
                diff_cost = track_info[2]
                
                # EntryからExitまでの回数
                trans_cnt+=1 
                
                # 結果出力                
                if PricePL >= 150:
                    result(PricePL, diff_ratio, diff_cost, timer, trans_time, profit, transaction)
                    profit += PricePL
                    transaction += 1
                    hold.append(track_diffAll)
                    hold.pop(0)                   
                    break
                elif timer >= TimeLeft:
                    result(PricePL, diff_ratio, diff_cost, timer, trans_time, profit, transaction)
                    profit += PricePL
                    transaction += 1
                    hold.append(track_diffAll)
                    hold.pop(0)                   
                    break
                else:
                    timer+=Time
                    trans_time+=Time
                    hold.append(track_diffAll)
                    hold.pop(0)                   
                    
                gc.collect()
                time.sleep(Time)

        elif diff_price < std_min:
            print("!!!Contrarian arbitrage!!!\n")

            def entry_bidL(): #最高値取引所のask価格でLong
                entry_vol = round(bet/Bbid_ask,8) # bet金額での初回購入量
                if exch_bid == "coincheck": 
                    entry_price = int(bet*(1+cc_long))
                else:
                    entry_price = bet # 初回BTCの販売金額
                return entry_vol, entry_price
            entry_info = entry_bidL()
            entry_vol = entry_info[0]
            entry_BLPrice = entry_info[1]
            print("Entry購入数量 "+str(entry_vol)+" 購入金額 "+str(entry_BLPrice))

            def entry_askS(): #最安値取引所のbid価格でShort
                if exch_ask == "coincheck": 
                    entry_price = int(Bask_bid*entry_vol*(1-cc_short))
                else:
                    entry_price = int(Bask_bid*entry_vol) # 初回BTCの売却金額
                return entry_price
            entry_ASPrice = entry_askS()
            print("Entry売却数量 "+str(entry_vol)+" 売却金額 "+str(entry_ASPrice))
            
            fp = first_pl(entry_ASPrice, entry_BLPrice)
            print("Entry値差 " + str(fp) +"\n")
            
            while True:
                # 最高値取引所のbid価格(売却予定金額)をtracking
                def track_bidL():
                    track_bidL = eval(exch_bid)()
                    track_Lask = track_bidL[0]
                    track_Lbid = track_bidL[1]
                    track_BLPrice = int(entry_vol * track_Lbid)
                    return exch_bid, track_Lask, track_Lbid, track_BLPrice 
                track_bidInfo = track_bidL()
                track_Bexch = track_bidInfo[0]
                track_Lask = track_bidInfo[1]
                track_Lbid = track_bidInfo[2]
                track_BLPrice = track_bidInfo[3]
                print(track_Bexch+" Tarcking 売却予定金額 "+str(track_BLPrice))
                
                # 最安値取引所のask価格(購入予定金額)をtracking
                def track_askS():
                    track_askS = eval(exch_ask)()
                    track_Sask = track_askS[0]
                    track_Sbid = track_askS[1]
                    track_ASPrice = int(entry_vol * track_Sask)
                    return exch_ask, track_Sask, track_Sbid, track_ASPrice
                track_askInfo = track_askS()
                track_Aexch = track_askInfo[0]
                track_Sask = track_askInfo[1]
                track_Sbid = track_askInfo[2]
                track_ASPrice = track_askInfo[3]
                print(track_Aexch+" Tarcking 購入予定金額 "+str(track_ASPrice))
                                
                # tracking different ratio
                diff_info = difference(track_Lbid, track_Sask, track_BLPrice, track_ASPrice, track_Lbid, track_Sask)
                track_diff = diff_info[0]
                track_diffPrice = diff_info[1] 
                track_diffAll = diff_info[2]
                print("取引所間値差",track_diffAll)

                # 利益予測
                track_info = pl_predict(entry_BLPrice, track_BLPrice, entry_ASPrice, track_ASPrice,\
                                        track_diff, track_diffPrice, ratio, diff_price)
                PricePL = track_info[0]
                diff_ratio = track_info[1]
                diff_cost = track_info[2]
                  
                # EntryからExitまでの回数
                trans_cnt+=1

                # 結果出力                
                if PricePL >= 200:
                    result(PricePL, diff_ratio, diff_cost, timer, trans_time, profit, transaction)
                    profit += PricePL
                    transaction += 1
                    hold.append(track_diffAll)
                    hold.pop(0)                   
                    break
                elif timer >= TimeLeft:
                    result(PricePL, diff_ratio, diff_cost, timer, trans_time, profit, transaction)
                    profit += PricePL
                    transaction += 1
                    hold.append(track_diffAll)
                    hold.pop(0)                   
                    break
                else:
                    timer+=Time
                    trans_time+=Time
                    hold.append(track_diffAll)
                    hold.pop(0)                   

                # std holdを更新し続ける
                gc.collect()
                time.sleep(Time)

        else:
            print("Nothing excahnge-pair\n")
            hold_times += 1
            gc.collect()
            
        msg2 = "合計利益 "+str(profit)+" 取引回数 "+str(transaction)+"/"+str(trans_cnt)+" Entry後約定時間 "+str(trans_time)+"\n"
        #logger.log(20,msg2)
        print(msg2)
        gc.collect()
        time.sleep(Time)

if __name__ == "__main__":
    logging.basicConfig()
    main()