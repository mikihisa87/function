import sys, os
sys.path.append(os.pardir)
from datetime import datetime, timezone, timedelta
import api_poloniex as api
from ModelSelect import alto_indicator as ind
from pandas_highcharts.display import display_charts
from IPython.display import display
import alto_data
import pandas as pd
import numpy as np
pd.options.display.max_rows = 8000

#ETH,XRP,DOGE,LTC,STR,XMR,BTS,DASH,MAID,FCT,CLAM
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
ohlc.tail()

#condition
Initial = 10000 #$
bet = 1000 #取引額
spread = 0.0015 * bet #手数料
pip = 0.0001 
diff = pip * 10 #利確、損切り価格差
lots = 200.27 #取引量 毎回$1,000分

#Resist
rn = 2
Resist = ind.iResist(ohlc, rn)

#Resist MA
rmn = 6
rma = ind.iResistMA(Resist, rmn)
rma_df = pd.DataFrame(rma)
rma_df.rename(columns={"Resist":"RMA"}, inplace=True)

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

#strategy #resist
BuyEntry = (
    ((Close > Resist) & (Close > up_sigma) & (Resist > Resist.shift())) 
    | ((Close > Resist) & (Volume > Volume.shift()*2))
    ).values
BuyExit = (
    ((Close <= up_sigma) 
    & (BandWidth <= bma) 
    & (Volume <= vma) 
    & (Close <= Close.shift())
    & (mfi <= 35)
    & (Resist <= Resist.shift()))
    | (Close <= Close.shift() * 0.95)
    | (Close <= Close.shift(3) * 0.925)
    | (Close <= Close.shift(6) * 0.9)
    ).values    

#Back test
N = len(ohlc) #FXデータのサイズ
BuyExit[N-2] = True #最後に強制エグジット
BuyPrice = 0.0 #売買価格

LongTrade = np.zeros(N) # 買いトレード情報
LongTradeQ = np.zeros(N)
LongPL = np.zeros(N) # 買いポジションの損益
LongPLQ = np.zeros(N)

for i in range(0,N):
    if BuyEntry[i] and BuyPrice == 0: #買いエントリーシグナル
        BuyPrice = Close[i]#Open[i+1]
        BuyQ = bet / BuyPrice #購入数量
        LongTrade[i] = BuyPrice #買いポジションオープン
        LongTradeQ[i] = BuyQ
        
    elif BuyExit[i] and BuyPrice != 0: #買いエグジットシグナル
        ClosePrice = Close[i]
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
RealProfit = Profit - Spread

print("period:", period_)
print('売買数 :', LongTrades*2)
print('買い数 :', LongTrades)
print("BuyRate:", buyrate, "%")
print('勝数 :', LongWinTrades)
print('最大勝 $:', LongPL.max())
print('平均勝 $:', round(LongPL.clip_lower(0).sum()/LongWinTrades, 2))
print('負数 :', LongLoseTrades)
print('最大負 $:', LongPL.min())
print('平均負 $:', round(LongPL.clip_upper(0).sum()/LongLoseTrades, 2))
print('平均損益 $:', round((AveProLong) ,2))
print('勝率 :', round(LongWinTrades/LongTrades*100, 2), "%")
print("手数料 $：", Spread, "\n")
print("結果")
print('総損益 $:', round(Profit, 2))
print('総損益(手数料込) $:', round(RealProfit, 2))
print('ROI :', round(ROI, 2),'%')
print('総利益 $:', round(GrossProfit, 2))
print('総損失 $:', round(GrossLoss, 2))

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
position = pd.DataFrame({"Close":Close[1:], "Long":long[1:], "Resist":Resist[1:]}) position = position[3000:4000]
display_charts(position, title="Position", figsize=(600,400), chart_type="stock", grid=True)
Bdiff = pd.DataFrame(Bdiff)
bollin_df = bollin.drop(["Band"], axis=1)