import requests
import sys, os
sys.path.append(os.pardir)
from datetime import datetime, timezone, timedelta
import api_poloniex as api
from ModelSelect import alto_indicator as ind
from ModelSelect import backtest as bt
from ModelSelect import data_base as db
from ModelSelect import charts as ch
from ModelSelect import result
from ModelSelect import TakeCutPL as tc
from pandas_highcharts.display import display_charts
from ipywidgets import interact
from IPython.display import display
import alto_data
import pandas as pd
import numpy as np
import csv
import warnings
warnings.filterwarnings("ignore")
pd.options.display.max_rows = 8000
pd.options.display.max_columns = 30

#making CSV
def settle(currency, period, kind):
    if kind == "Crypto":
        currency = currency
        period = period
        start = datetime(2017,3,1,0,0,0).strftime("%s") 
        end = datetime(2018,1,29,0,0,0).strftime("%s")
        url = api.select(currency, api.unix(start), api.unix(end), period)
        try:
            get = api.get_currency(url)
            path = "./{}.csv".format(currency)
            get.to_csv(path)
        except:
            print("Please select pull-down menu")
    else:
        start_us = datetime(2017,3,1,0,0,0).strftime("%s") 
        end_us = datetime(2018,1,29,0,0,0).strftime("%s")
        try:
            url = api.dollers("USDT", api.unix(start_us), api.unix(end_us), period)
            usd_get = api.get_usd(url)
            #path = "./alto_data/"
            path = "./USDT.csv"
            usd_get.to_csv(path)
        except:
            print("Please select only period")
            
interact(settle, 
         kind=["Crypto", "USDT"],
         currency=["", "ETH","XRP","LTC","DOGE","STR","XMR","BTS","DASH","MAID","FCT","CLAM"],
         period=["", "300", "900", "1800", "7200", "14400", "86400"]);
         
#ETH,XRP,LTC / DOGE,STR,XMR,BTS,DASH,MAID,FCT,CLAM
SelectAlto = "ETH"
path_r = "./{}.csv".format(SelectAlto)
df = pd.read_csv(path_r) 
Time = df["Time"]
df = df.set_index("Time")
usd = pd.read_csv("./USDT.csv")
usd = usd.set_index("us_Time")
data = pd.concat([df, usd], axis=1)
data["High"] = data.apply(lambda x: x.iloc[0]*x.iloc[5], axis=1)
data["Low"] = data.apply(lambda x : x.iloc[1]*x.iloc[6], axis=1)
data["Open"] = data.apply(lambda x : x.iloc[2]*x.iloc[7], axis=1)
data["Close"] = data.apply(lambda x : x.iloc[3]*x.iloc[8], axis=1)

ohlc = data.drop(data.columns[[4,5,6,7,8]], axis=1)
Open = ohlc["Open"]
Close = ohlc["Close"]
High = ohlc["High"]
Low = ohlc["Low"]
Volume = ohlc["us_Volume"]
ohlc.head()

#Resist
rn = 2
Resist = ind.iResist(ohlc, rn)

#Resist MA
rmn = 6
rma = ind.iResistMA(Resist, rmn)
rma_df = pd.DataFrame(rma)
rma_df.rename(columns={"Resist":"RMA"}, inplace=True)

#Support
sn = 2
Support = ind.iSupport(ohlc, sn)

#Support MA
smn = 6
sma = ind.iSupportMA(Support, smn)
sma_df = pd.DataFrame(sma)
sma_df.rename(columns={"Support":"SuMA"}, inplace=True)

#Bollinger
bollin = ind.iBands(ohlc, 20, 2)
up_sigma = bollin["Upper"]
low_sigma = bollin["Lower"]

#Volume MA
vmn = 3
vma = ind.iVolumeMA(Volume, vmn)
vma_df = pd.DataFrame(vma)
vma_df.rename(columns={"us_Volume":"VMA"}, inplace=True)

#MFI
mn = 14
mfi = ind.iMFI(Close,High,Low,Volume,mn,Time)

#MACD
macd = ind.iMACD(ohlc, 12, 26, 9)
main = macd["Main"]
signal = macd["Signal"]

#RSI
rsi = ind.iRSI(ohlc, 14)
rsi_df = pd.DataFrame(rsi)
rsi_df.rename(columns={0:"RSI"}, inplace=True)

#DMI
adx = ind.iADX(ohlc, 14)
pdi = adx["PlusDI"]
mdi = adx["MinusDI"]
main = adx["Main"]
mdi_df = pd.DataFrame(mdi)
pdi_df = pd.DataFrame(pdi)
mdi_df.rename(columns={0:"MDI"}, inplace=True)
pdi_df.rename(columns={0:"PDI"}, inplace=True)
MDI = pd.concat([mdi_df, pdi_df], axis=1)

#Momentum
mom = ind.iMomentum(ohlc, 10)

#ICHIMOKU
ichimoku = ind.iIchimoku(ohlc, 9, 10, 52)
tenkan = ichimoku["Tenkan"] 
kijun = ichimoku["Kijun"]
senkou1 = ichimoku["SenkouA"]
senkou2 = ichimoku["SenkouB"]
chikou = ichimoku["Chikou"]

#SAR
sar = ind.iSAR(ohlc, 0.002, 0.24) #df,step,acc_maximum

#Band width ratio
bollin = pd.DataFrame({"Close":Close, "UpSigma":up_sigma, "LowSigma":low_sigma})
bollin["Band"] = bollin.apply(lambda x: x["UpSigma"] - x["LowSigma"], axis=1)
BandWidth = bollin["Band"]
bollin["Band_bef"] = bollin["Band"].shift()
bollin["Bdiff"] = bollin.apply(lambda x: (x["Band"] / x["Band_bef"])*100, axis=1)
Bdiff = bollin["Bdiff"]

#Band width ratio MA
brn = 50
brma = Bdiff.rolling(window=brn).mean()
brma_df = pd.DataFrame(brma)
brma_df.rename(columns={"Bdiff":"BRMA"}, inplace=True)

#Band MA
bn = 10
bma = BandWidth.rolling(window=bn).mean()
bma_df = pd.DataFrame(bma)
bma_df.rename(columns={"Band":"BMA"}, inplace=True)
bma_df["Band"] = BandWidth

"""
テスト全体 without 指値
"""
Open = ohlc.Open #始値
Low = ohlc.Low #安値
High = ohlc.High #高値
Close = ohlc.Close
Volume = ohlc.us_Volume

#Condition 
Initial = 10000 # 初期資産
TP=0
SL=0
spread=0.002
#commision = 0.002
Lots = 1 #実際の売買量

#Strategy
FastMA = ind.iMA(ohlc, 10) #エントリー用短期移動平均
SlowMA = ind.iMA(ohlc, 30) #エントリー用長期移動平均
ExitMA = ind.iMA(ohlc, 5) #エグジット用移動平均
BuyEntry = ((FastMA > SlowMA) & (FastMA.shift() <= SlowMA.shift())).values
BuyExit = ((ohlc.Close < ExitMA) & (ohlc.Close.shift() >= ExitMA.shift())).values


N = len(ohlc) #FXデータのサイズ
LongTrade = np.zeros(N) #買いトレード情報
ShortTrade = np.zeros(N) #売りトレード情報

#買いエントリー価格
BuyEntryS = np.hstack((False, BuyEntry[:-1])) #買いエントリーシグナルのシフト
LongTrade[BuyEntryS] = Open[BuyEntryS]#*(1+(commision+spread)) #成行買い

#買いエグジット価格
BuyExitS = np.hstack((False, BuyExit[:-2], True)) #買いエグジットシグナルのシフト
LongTrade[BuyExitS] = -Open[BuyExitS]#*(1-commision)

LongPL = np.zeros(N) # 買いポジションの損益
ShortPL = np.zeros(N) # 売りポジションの損益
BuyPrice = 0 # 売買価格
SellPrice = 0 

#売買条件
for i in range(1,N):
    if LongTrade[i] > 0: #買いエントリーシグナル
        if BuyPrice == 0:
            BuyPrice = LongTrade[i]
            ShortTrade[i] = -BuyPrice #売りエグジット
        else:
            LongTrade[i] = 0
            
    if LongTrade[i] < 0: #買いエグジットシグナル
        if BuyPrice != 0:
            LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
            BuyPrice = 0
        else:
            LongTrade[i] = 0
            
    if ShortTrade[i] > 0: #売りエントリーシグナル
        if SellPrice == 0:
            SellPrice = ShortTrade[i]
            LongTrade[i] = -SellPrice #買いエグジット
        else: 
            ShortTrade[i] = 0

    if ShortTrade[i] < 0: #売りエグジットシグナル
        if SellPrice != 0:
            ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
            SellPrice = 0
        else: 
            ShortTrade[i] = 0

#利確・損切り条件
    if BuyPrice != 0 and SL > 0: #SLによる買いポジションの決済
        StopPrice = BuyPrice*(1-(SL/100))
        if Low[i] <= StopPrice:
            LongTrade[i] = -StopPrice
            LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
            BuyPrice = 0

    if BuyPrice != 0 and TP > 0: #TPによる買いポジションの決済
        LimitPrice = BuyPrice*(1+(TP/100))
        if High[i] >= LimitPrice:
            LongTrade[i] = -LimitPrice
            LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
            BuyPrice = 0

    if SellPrice != 0 and SL > 0: #SLによる売りポジションの決済
        StopPrice = SellPrice*(1+(SL/100))
        if High[i] >= StopPrice:
            ShortTrade[i] = -StopPrice
            ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
            SellPrice = 0

    if SellPrice != 0 and TP > 0: #TPによる売りポジションの決済
        LimitPrice = SellPrice*(1-(TP/100))
        if Low[i] <= LimitPrice:
            ShortTrade[i] = -LimitPrice
            ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
            SellPrice = 0

Trade = pd.DataFrame({'Long':LongTrade, 'Short':ShortTrade}, index=ohlc.index)
PL = pd.DataFrame({'Long':LongPL, 'Short':ShortPL}, index=ohlc.index)

LongPL = PL['Long']
LongTrades = np.count_nonzero(Trade['Long'])//2
LongWinTrades = np.count_nonzero(LongPL.clip_lower(0))
LongLoseTrades = np.count_nonzero(LongPL.clip_upper(0))
print('買いトレード数 =', LongTrades)
print('勝トレード数 =', LongWinTrades)
print('最大勝トレード =', LongPL.max())
print('平均勝トレード =', round(LongPL.clip_lower(0).sum()/LongWinTrades, 2))
print('負トレード数 =', LongLoseTrades)
print('最大負トレード =', LongPL.min())
print('平均負トレード =', round(LongPL.clip_upper(0).sum()/LongLoseTrades, 2))
print('勝率 =', round(LongWinTrades/LongTrades*100, 2), '%\n')

ShortPL = PL['Short']
ShortTrades = np.count_nonzero(Trade['Short'])//2
ShortWinTrades = np.count_nonzero(ShortPL.clip_lower(0))
ShortLoseTrades = np.count_nonzero(ShortPL.clip_upper(0))
print('売りトレード数 =', ShortTrades)
print('勝トレード数 =', ShortWinTrades)
print('最大勝トレード =', ShortPL.max())
print('平均勝トレード =', round(ShortPL.clip_lower(0).sum()/ShortWinTrades, 2))
print('負トレード数 =', ShortLoseTrades)
print('最大負トレード =', ShortPL.min())
print('平均負トレード =', round(ShortPL.clip_upper(0).sum()/ShortLoseTrades, 2))
print('勝率 =', round(ShortWinTrades/ShortTrades*100, 2), '%\n')

Trades = LongTrades

WinTrades = LongWinTrades+ShortWinTrades
LoseTrades = LongLoseTrades+ShortLoseTrades
print('総トレード数 =', Trades)
print('勝トレード数 =', WinTrades)
print('最大勝トレード =', max(LongPL.max(), ShortPL.max()))
print('平均勝トレード =', round((LongPL.clip_lower(0).sum()+ShortPL.clip_lower(0).sum())/WinTrades, 2))
print('負トレード数 =', LoseTrades)
print('最大負トレード =', min(LongPL.min(), ShortPL.min()))
print('平均負トレード =', round((LongPL.clip_upper(0).sum()+ShortPL.clip_upper(0).sum())/LoseTrades, 2))
print('勝率 =', round(WinTrades/Trades*100, 2), '%\n')

GrossProfit = LongPL.clip_lower(0).sum()
GrossLoss = LongPL.clip_upper(0).sum()
Profit = GrossProfit+GrossLoss
Equity = (LongPL).cumsum()
MDD = (Equity.cummax()-Equity).max()
print('総利益 =', round(GrossProfit, 2))
print('総損失 =', round(GrossLoss, 2))
print('総損益 =', round(Profit, 2))
print('プロフィットファクター =', round(-GrossProfit/GrossLoss, 2))
print('平均損益 =', round(Profit/Trades, 2))
print('最大ドローダウン =', round(MDD, 2))
print('リカバリーファクター =', round(Profit/MDD, 2))
Equity = Trade, PL

#Position        
def PositionLine(trade):
    PosPeriod = 0 #ポジションの期間
    Position = False #ポジションの有無
    Line = trade.copy()
    for i in range(len(Line)):
        if trade[i] > 0: 
            Position = True 
        elif Position: 
            PosPeriod += 1 # ポジションの期間をカウント
        if trade[i] < 0:
            if PosPeriod > 0:
                Line[i] = -trade[i]
                diff = (Line[i]-Line[i-PosPeriod])/PosPeriod
                for j in range(i-1, i-PosPeriod, -1):
                    Line[j] = Line[j+1]-diff # ポジションの期間を補間
                PosPeriod = 0
                Position = False
        if trade[i] == 0 and not Position:
            Line[i] = 'NaN'
    return Line

plot = pd.DataFrame({'Equity':Equity+Initial})
display_charts(plot[:1000], chart_type="stock", title="Position", figsize=(640,480), grid=True)
long1 = Trade["Long"]
short1 = Trade["Short"]
long = PositionLine(long1)
short = PositionLine(short1)

#Chart
position = pd.DataFrame({"Open":Open, "Long":long}) #"Short":short, position = position[:1000]
display_charts(position, title="Position", figsize=(600,400), chart_type="stock", grid=True)

"""
テスト 全体
"""

TP=100
SL=50
Limit=20
lots=0.1
spread=2
TP=0
SL=0
Limit=0
Expiration=10

FastMA = ind.iMA(ohlc, 10) #エントリー用短期移動平均
SlowMA = ind.iMA(ohlc, 30) #エントリー用長期移動平均
ExitMA = ind.iMA(ohlc, 5) #エグジット用移動平均z

#買いエントリーシグナル
BuyEntry = ((FastMA > SlowMA) & (FastMA.shift() <= SlowMA.shift())).values
#売りエントリーシグナル
SellEntry = ((FastMA < SlowMA) & (FastMA.shift() >= SlowMA.shift())).values
#買いエグジットシグナル
BuyExit = ((ohlc.Close < ExitMA) & (ohlc.Close.shift() >= ExitMA.shift())).values
#売りエグジットシグナル
SellExit = ((ohlc.Close > ExitMA) & (ohlc.Close.shift() <= ExitMA.shift())).values

Open = ohlc.Open.values #始値
Low = ohlc.Low.values #安値
High = ohlc.High.values #高値
Point = 0.0001 #1pipの値
if(Open[0] > 50):
    Point = 0.01 #クロス円の1pipの値
Spread = spread*Point #スプレッド
Lots = lots*100000 #実際の売買量
N = len(ohlc) #FXデータのサイズ

LongTrade = np.zeros(N) #買いトレード情報
ShortTrade = np.zeros(N) #売りトレード情報

#買いエントリー価格
BuyEntryS = np.hstack((False, BuyEntry[:-1])) #買いエントリーシグナルのシフト
if Limit == 0:
    LongTrade[BuyEntryS] = Open[BuyEntryS]+Spread #成行買い
else: #指値買い
    for i in range(N-Expiration):
        if BuyEntryS[i]:
            BuyLimit = Open[i]-Limit*Point #指値
            for j in range(Expiration):
                if Low[i+j] <= BuyLimit: #約定条件
                    LongTrade[i+j] = BuyLimit+Spread
                    break
    
#買いエグジット価格
BuyExitS = np.hstack((False, BuyExit[:-2], True)) #買いエグジットシグナルのシフト
LongTrade[BuyExitS] = -Open[BuyExitS]

#売りエントリー価格
SellEntryS = np.hstack((False, SellEntry[:-1])) #売りエントリーシグナルのシフト
if Limit == 0: ShortTrade[SellEntryS] = Open[SellEntryS] #成行売り
else: #指値売り
    for i in range(N-Expiration):
        if SellEntryS[i]:
            SellLimit = Open[i]+Limit*Point #指値
            for j in range(Expiration):
                if High[i+j] >= SellLimit: #約定条件
                    ShortTrade[i+j] = SellLimit
                    break
print(pd.DataFrame(LongTrade))                

#売りエグジット価格
SellExitS = np.hstack((False, SellExit[:-2], True)) #売りエグジットシグナルのシフト
ShortTrade[SellExitS] = -(Open[SellExitS]+Spread)

LongPL = np.zeros(N) # 買いポジションの損益
ShortPL = np.zeros(N) # 売りポジションの損益
BuyPrice = SellPrice = 0.0 # 売買価格

for i in range(1,N):
    if LongTrade[i] > 0: #買いエントリーシグナル
        if BuyPrice == 0:
            BuyPrice = LongTrade[i]
            ShortTrade[i] = -BuyPrice #売りエグジット
        else: LongTrade[i] = 0

    if ShortTrade[i] > 0: #売りエントリーシグナル
        if SellPrice == 0:
            SellPrice = ShortTrade[i]
            LongTrade[i] = -SellPrice #買いエグジット
        else: ShortTrade[i] = 0

    if LongTrade[i] < 0: #買いエグジットシグナル
        if BuyPrice != 0:
            LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
            BuyPrice = 0
        else: LongTrade[i] = 0

    if ShortTrade[i] < 0: #売りエグジットシグナル
        if SellPrice != 0:
            ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
            SellPrice = 0
        else: ShortTrade[i] = 0

    if BuyPrice != 0 and SL > 0: #SLによる買いポジションの決済
        StopPrice = BuyPrice-SL*Point
        if Low[i] <= StopPrice:
            LongTrade[i] = -StopPrice
            LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
            BuyPrice = 0

    if BuyPrice != 0 and TP > 0: #TPによる買いポジションの決済
        LimitPrice = BuyPrice+TP*Point
        if High[i] >= LimitPrice:
            LongTrade[i] = -LimitPrice
            LongPL[i] = -(BuyPrice+LongTrade[i])*Lots #損益確定
            BuyPrice = 0

    if SellPrice != 0 and SL > 0: #SLによる売りポジションの決済
        StopPrice = SellPrice+SL*Point
        if High[i] >= StopPrice+Spread:
            ShortTrade[i] = -StopPrice
            ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
            SellPrice = 0

    if SellPrice != 0 and TP > 0: #TPによる売りポジションの決済
        LimitPrice = SellPrice-TP*Point
        if Low[i] <= LimitPrice+Spread:
            ShortTrade[i] = -LimitPrice
            ShortPL[i] = (SellPrice+ShortTrade[i])*Lots #損益確定
            SellPrice = 0

Trade = pd.DataFrame({'Long':LongTrade, 'Short':ShortTrade}, index=ohlc.index)
PL = pd.DataFrame({'Long':LongPL, 'Short':ShortPL}, index=ohlc.index)

LongPL = PL['Long']
LongTrades = np.count_nonzero(Trade['Long'])//2
LongWinTrades = np.count_nonzero(LongPL.clip_lower(0))
LongLoseTrades = np.count_nonzero(LongPL.clip_upper(0))
print('買いトレード数 =', LongTrades)
print('勝トレード数 =', LongWinTrades)
print('最大勝トレード =', LongPL.max())
print('平均勝トレード =', round(LongPL.clip_lower(0).sum()/LongWinTrades, 2))
print('負トレード数 =', LongLoseTrades)
print('最大負トレード =', LongPL.min())
print('平均負トレード =', round(LongPL.clip_upper(0).sum()/LongLoseTrades, 2))
print('勝率 =', round(LongWinTrades/LongTrades*100, 2), '%\n')

ShortPL = PL['Short']
ShortTrades = np.count_nonzero(Trade['Short'])//2
ShortWinTrades = np.count_nonzero(ShortPL.clip_lower(0))
ShortLoseTrades = np.count_nonzero(ShortPL.clip_upper(0))
print('売りトレード数 =', ShortTrades)
print('勝トレード数 =', ShortWinTrades)
print('最大勝トレード =', ShortPL.max())
print('平均勝トレード =', round(ShortPL.clip_lower(0).sum()/ShortWinTrades, 2))
print('負トレード数 =', ShortLoseTrades)
print('最大負トレード =', ShortPL.min())
print('平均負トレード =', round(ShortPL.clip_upper(0).sum()/ShortLoseTrades, 2))
print('勝率 =', round(ShortWinTrades/ShortTrades*100, 2), '%\n')

Trades = LongTrades + ShortTrades
WinTrades = LongWinTrades+ShortWinTrades
LoseTrades = LongLoseTrades+ShortLoseTrades
print('総トレード数 =', Trades)
print('勝トレード数 =', WinTrades)
print('最大勝トレード =', max(LongPL.max(), ShortPL.max()))
print('平均勝トレード =', round((LongPL.clip_lower(0).sum()+ShortPL.clip_lower(0).sum())/WinTrades, 2))
print('負トレード数 =', LoseTrades)
print('最大負トレード =', min(LongPL.min(), ShortPL.min()))
print('平均負トレード =', round((LongPL.clip_upper(0).sum()+ShortPL.clip_upper(0).sum())/LoseTrades, 2))
print('勝率 =', round(WinTrades/Trades*100, 2), '%\n')

GrossProfit = LongPL.clip_lower(0).sum()+ShortPL.clip_lower(0).sum()
GrossLoss = LongPL.clip_upper(0).sum()+ShortPL.clip_upper(0).sum()
Profit = GrossProfit+GrossLoss
Equity = (LongPL+ShortPL).cumsum()
MDD = (Equity.cummax()-Equity).max()
print('総利益 =', round(GrossProfit, 2))
print('総損失 =', round(GrossLoss, 2))
print('総損益 =', round(Profit, 2))
print('プロフィットファクター =', round(-GrossProfit/GrossLoss, 2))
print('平均損益 =', round(Profit/Trades, 2))
print('最大ドローダウン =', round(MDD, 2))
print('リカバリーファクター =', round(Profit/MDD, 2))
Equity = Trade, PL

#Position        
def PositionLine(trade):
    PosPeriod = 0 #ポジションの期間
    Position = False #ポジションの有無
    Line = trade.copy()
    for i in range(len(Line)):
        if trade[i] > 0: 
            Position = True 
        elif Position: 
            PosPeriod += 1 # ポジションの期間をカウント
        if trade[i] < 0:
            if PosPeriod > 0:
                Line[i] = -trade[i]
                diff = (Line[i]-Line[i-PosPeriod])/PosPeriod
                for j in range(i-1, i-PosPeriod, -1):
                    Line[j] = Line[j+1]-diff # ポジションの期間を補間
                PosPeriod = 0
                Position = False
        if trade[i] == 0 and not Position:
            Line[i] = 'NaN'
    return Line

plot = pd.DataFrame({'Equity':Equity+Initial})
display_charts(plot[:1000], chart_type="stock", title="Position", figsize=(640,480), grid=True)
long1 = Trade["Long"]
short1 = Trade["Short"]
long = PositionLine(long1)
short = PositionLine(short1)

#Chart
position = pd.DataFrame({"Close":Open, "Long":long, "Short":short}) #"Short":short, position = position[:1000]
display_charts(position, title="Position", figsize=(600,400), chart_type="stock", grid=True)