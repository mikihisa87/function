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
            path = "./USDT.csv"
            usd_get.to_csv(path)
        except:
            print("Please select only period")
            
interact(settle, 
         kind=["Crypto", "USDT"],
         currency=["", "ETH","XRP","LTC","DOGE","STR","XMR","BTS","DASH","MAID","FCT","CLAM"],
         period=["", "300", "900", "1800", "7200", "14400", "86400"]);
         
#ETH,XRP,LTC / DOGE,STR,XMR,BTS,DASH,MAID,FCT,CLAM
SelectAlto = "XRP"
path_r = "./{}.csv".format(SelectAlto)
df = pd.read_csv(path_r) 
Time = df["Time"]
df = df.set_index("Time")
usd = pd.read_csv("./alto_data/USDT.csv")
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

#condition
Initial = 10000 #$
bet = 1000 #取引額
spread = 0.0015 * bet #手数料
pip = 0.0001 
diff = pip * 10 #利確、損切り価格差
lots = 200.27 #取引量 毎回$1,000分
commision = 0.002 * bet

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
Long
"""
#strategy
BuyEntry = (
    ((Close > Resist) & (Close > up_sigma) & (Resist > Resist.shift())) 
    | ((Close > Resist) & (Volume > Volume.shift()*2) & (Close > up_sigma) & (mfi > 75))
    | ((Close < low_sigma))
    ).values

"""利確・損切り定義"""
diff = 3
PTrade = tc.single(diff, Close, BuyEntry,Time)[0]
MTrade = tc.single(diff, Close, BuyEntry,Time)[1]
DPTrade = tc.double(diff, Close, BuyEntry,Time)[0]
DMTrade = tc.double(diff, Close, BuyEntry,Time)[1]

BuyExit = (
    ((Close <= Resist) 
    & (Close <= up_sigma) 
    & (BandWidth <= bma) 
    & (Volume <= vma) 
    & (Close <= Close.shift())
    & (mfi <= 25)
    & (Resist <= Resist.shift()))
#    | (Close <= Close.shift() * 0.95)
#    | (Close >= PTrade)
    | (Close <= MTrade)
#    (Close >= DPTrade)
#    | (Close <= DMTrade)
    ).values    
    
#Back test
N = len(ohlc) #FXデータのサイズ
BuyExit[N-2] = True #最後に強制エグジット
BuyPrice = 0.0 #売買価格

LongTrade = np.zeros(N) # 買いトレード情報
LongTradeQ = np.zeros(N)
LongPL = np.zeros(N) # 買いポジションの損益
LongPLQ = np.zeros(N)

for i in range(N):
    if BuyEntry[i] and BuyPrice == 0: #買いエントリーシグナル
        BuyPrice = Close[i]#Open[i+1]
        BuyQ = bet / BuyPrice #購入数量
        LongTrade[i] = BuyPrice #買いポジションオープン
        LongTradeQ[i] = BuyQ
        
    elif BuyExit[i] and BuyPrice != 0: #買いエグジットシグナル
        ClosePrice = Close[i]#Back test
        LongTrade[i] = -ClosePrice #買いポジションクローズ
        #LongPL[i] = (ClosePrice-BuyPrice)*lots #損益確定
        LongPL[i] = (ClosePrice-BuyPrice)*BuyQ #損益確定
        BuyPrice = 0
        
Trade = pd.DataFrame({'Long':LongTrade}, index=ohlc.index)
PL = pd.DataFrame({'Long':LongPL}, index=ohlc.index)

#Result
LongPL = PL['Long']
LongPLResult = LongPL.sum()
LongTrades = np.count_nonzero(Trade['Long'])//2
LongWinTrades = np.count_nonzero(LongPL.clip_lower(0))
LongLoseTrades = np.count_nonzero(LongPL.clip_upper(0))
try:
    AveProLong = LongPLResult / LongTrades
except:
    print("Error")

Trades = LongTrades
WinTrades = LongWinTrades
LoseTrades = LongLoseTrades
AssetChart = (LongPL).cumsum()

GrossProfit = LongPL.clip_lower(0).sum()
GrossLoss = LongPL.clip_upper(0).sum()
Profit = GrossProfit+GrossLoss
AvePro = Profit / Trades
Equity = LongPL.cumsum()
Asset = Initial + Profit
ROI = (Asset - Initial) / Initial * 100
trades_ = Trade.any(axis=1).sum()
period_ = Trade.shape[0]
buyrate = round((LongTrades / period_)*100, 1)
Spread = spread * LongTrades*2
Commision = commision * LongTrades*2
RealProfit = Profit - Spread - Commision

print("period:", period_)
LongTrades_ = LongTrades*2
print('売買数 :', LongTrades_)
print('買い数 :', LongTrades)
print("BuyRate:", buyrate, "%")
print('勝数 :', LongWinTrades)
MaxPL_ = round(LongPL.max(), 2)
print('最大勝 $:', MaxPL_)
AveWin_ = round(LongPL.clip_lower(0).sum()/LongWinTrades, 2)
print('平均勝 $:', AveWin_)
print('負数 :', LongLoseTrades)
MinPL_ = round(LongPL.min(), 2)
print('最大負 $:', MinPL_)
AveLose_ = round(LongPL.clip_upper(0).sum()/LongLoseTrades, 2)
print('平均負 $:', AveLose_)
AvePL_ = round((AveProLong) ,2)
print('平均損益 $:', AvePL_)
WinRate_ = round(LongWinTrades/LongTrades*100, 2)
print('勝率 :', WinRate_, "%")
print("手数料 $：", Spread, "\n")
print("結果")
Profit_ = round(Profit, 2)
print('総損益 $:', Profit_)
RealProfit_ = round(RealProfit, 2)
print('総損益(手数料込) $:', RealProfit_)
ROI_ = round(ROI, 2)
print('ROI :', ROI_,'%')
GrossProfit_ = round(GrossProfit, 2)
print('総利益 $:', GrossProfit_)
GrossLoss_ = round(GrossLoss, 2)
print('総損失 $:', GrossLoss_)

#Position
def Position(trade):
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

long1 = Trade["Long"]
long = Position(long1)

#Chart
position = pd.DataFrame({"Close":Close[1:], "Long":long[1:]}) #"Short":short, "UpSigma":UpSigma, "LowSigma":LowSigma
position = position[88000:89000]
display_charts(position, title="Position", figsize=(600,400), chart_type="stock", grid=True)