import numpy as np
import pandas as pd

def Words(tech):
    holds = []
    for i in range(len(tech)):
        if "a" <= tech[i] <="z":
            a = tech[i].upper()
            holds.append(a)
        else:
            b = tech[i]
            holds.append(b)

    hold = ''.join(holds)
    return hold

def Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread, apply="Close"):
    #for hold
    Close = ohlc[apply].values # 終値
    start_price = Close[0]
    end_price = Close[-1]
    diff = end_price - start_price
    HoldProfit = (diff * lots) - spread
    
    Open = ohlc["Open"].values #始値
    Spread = spread #手数料
    Lots = lots #実際の売買量
    N = len(ohlc) #FXデータのサイズ
    BuyExit[N-2] = True #最後に強制エグジット
    SellExit[N-2] = True 
    BuyPrice = 0.0 #売買価格
    SellPrice = 0.0 

    LongTrade = np.zeros(N) # 買いトレード情報
    ShortTrade = np.zeros(N) # 売りトレード情報

    LongPL = np.zeros(N) # 買いポジションの損益
    ShortPL = np.zeros(N) # 売りポジションの損益

    for i in range(1,N):
        if BuyEntry[i-1] and BuyPrice == 0: #買いエントリーシグナル
            BuyPrice = Open[i]+Spread
            LongTrade[i] = BuyPrice #買いポジションオープン
        elif BuyExit[i-1] and BuyPrice != 0: #買いエグジットシグナル
            ClosePrice = Open[i]
            LongTrade[i] = -ClosePrice #買いポジションクローズ
            LongPL[i] = (ClosePrice-BuyPrice)*Lots #損益確定
            BuyPrice = 0

        if SellEntry[i-1] and SellPrice == 0: #売りエントリーシグナル
            SellPrice = Open[i]
            ShortTrade[i] = SellPrice #売りポジションオープン
        elif SellExit[i-1] and SellPrice != 0: #売りエグジットシグナル
            ClosePrice = Open[i]+Spread
            ShortTrade[i] = -ClosePrice #売りポジションクローズ
            ShortPL[i] = (SellPrice-ClosePrice)*Lots #損益確定
            SellPrice = 0

    return pd.DataFrame({'Long':LongTrade, 'Short':ShortTrade}, index=ohlc.index),            pd.DataFrame({'Long':LongPL, 'Short':ShortPL}, index=ohlc.index),    HoldProfit