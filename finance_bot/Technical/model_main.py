from ModelSelect import indicators as ind
from ModelSelect import backtest as bt
from ModelSelect import data_base as db
from ModelSelect import charts as ch
from ModelSelect import result
from pandas_highcharts.display import display_charts
from ipywidgets import interact
import matplotlib.pyplot as plt
%matplotlib inline
import pandas as pd
import numpy as np

df = db.prices('1 minutes', 'BTC_JPY', '2017-01-01 09:00:00', '2017-06-01 09:00:00', 0, 41976)
# get rid of outlier
df = df[df[:]>=500000]
df = df.dropna()
df.rename(columns={"v_t":"Close", "v_hi":"High", "v_lo":"Low"}, inplace=True)
df = df.set_index("period")
df["Open"] = df["Close"].shift()

#時間足の変更
ohlc = ind.TF_ohlc(df, '5T')

#condition
pip = 0.001
lots = pip * 25
initial = 1000000
spread = 0
Open = ohlc["Open"]
Close = ohlc["Close"]
High = ohlc["High"]
Low = ohlc["Low"]
tech = "BOLLINGER RSI"
#technical bollinger
n = 20
deviation = 2
deviation2 = 2.5
sma = Close.rolling(window=n).mean()
sigma = Close.rolling(window=n).std(ddof=0)
upper_sigma = sma + sigma * deviation
upper_sigma2 = sma + sigma * deviation2
lower_sigma = sma - sigma * deviation
lower_sigma2 = sma - sigma * deviation2
#technical rsi
rsi = ind.iRSI(ohlc, 14)
#strategy 
for i in range(len(Low)):
    if Low[i] <= lower_sigma[i]:        
        SellExit = (BuyEntry.copy())     
        BuyEntry = (rsi <= 30).values
    elif Low[i] <= lower_sigma2[i]:  
        BuyExit = (SellEntry.copy()) 
        SellEntry = (Low <= lower_sigma2).values
    elif High[i] >= upper_sigma[i]:
        BuyExit = (SellEntry.copy()) 
        SellEntry = (rsi >= 70).values
    elif High[i] >= upper_sigma2[i]:
        SellExit = (BuyEntry.copy())     
        BuyEntry = (High >= upper_sigma2).values
        
#back test
Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
modelchart =  ({"High":High, "Low":Low, "Up_sigma":upper_sigma, "Low_sigma":lower_sigma})
modelchart2 =  ({"RSI":rsi})
modelchart = ch.ModelChart(modelchart, tech)
modelchart2 = ch.ModelChart(modelchart2, tech)
#position timing
long = ch.PositionLine(Trade["Long"])
short = ch.PositionLine(Trade["Short"])
position = ch.PositionChart(Open, long, short, tech) 

def Strategy(ohlc, lots, initial, spread):
    Open = ohlc["Open"]
    Close = ohlc["Close"]
    High = ohlc["High"]
    Low = ohlc["Low"]
    @interact(Trend=["", "SMA", "EMA", "BOLLINGERBAND", "SAR", "ICHIMOKU"],\
              Oscillator=["", "RSI", "STOCHASTIC", "ADX", "MACD", "MOMENTUM"])
    def technical(Trend, Oscillator):
        trend = Trend
        oscillator = Oscillator
        combine = trend + " " + oscillator
        tech = combine or oscillator or trend
        print(tech)
        #Combine tech:真ん中にスペース
        if tech == "BOLLINGERBAND RSI":
            #technical bollinger
            n = 20
            deviation = 2
            deviation2 = 2.5
            sma = Close.rolling(window=n).mean()
            sigma = Close.rolling(window=n).std(ddof=0)
            upper_sigma = sma + sigma * deviation
            upper_sigma2 = sma + sigma * deviation2
            lower_sigma = sma - sigma * deviation
            lower_sigma2 = sma - sigma * deviation2
            #technical rsi
            rsi = ind.iRSI(ohlc, 14)
            #strategy 
            BuyEntry = (
                (Low <= lower_sigma) & (Low.shift() > lower_sigma.shift())
                & (rsi <= 30)
            ).values
            SellEntry = (
                (High >= upper_sigma) & (High.shift() < upper_sigma.shift())
                & (rsi >= 70)
            ).values
            BuyExit = (SellEntry.copy()) 
            SellExit = (BuyEntry.copy())     
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"High":High, "Low":Low, "Up_sigma":upper_sigma, "Low_sigma":lower_sigma})
            modelchart2 =  ({"RSI":rsi})
            modelchart = ch.ModelChart(modelchart, tech)
            modelchart2 = ch.ModelChart(modelchart2, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 
            
        #Trend tech:後ろにスペース
        elif tech == "SMA ":
            #technical SMA
            fastma = ind.iMA(ohlc, 5)
            slowma = ind.iMA(ohlc, 10)
            #strategy SMA 順張り
            BuyEntry = ((fastma > slowma) & (fastma.shift() <= slowma.shift())).values
            SellEntry = ((fastma < slowma) & (fastma.shift() >= slowma.shift())).values
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Close":Close, "FastMA":fastma, "SlowMA":slowma})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 

        elif tech == "EMA ":
            #technical EMA
            fastema = ind.iDEMA(ohlc, 5)
            slowema = ind.iDEMA(ohlc, 10)
            #strategy EMA 順張り
            BuyEntry = ((fastema > slowema) & (fastema.shift() <= slowema.shift())).values
            SellEntry = ((fastema < slowema) & (fastema.shift() >= slowema.shift())).values
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Close":Close, "FastEMA":fastema, "SlowEMA":slowema})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 

        elif tech == "BOLLINGERBAND ":
            #technical BllingerBand 逆張り
            n = 20
            deviation = 2
#             print("Number of MA, Recommendation:20")
#             n = input() #移動平均足
            sma = Close.rolling(window=n).mean()
#             print("Number of deviation, Recommendation:2")
#             deviation = int(input()) #標準偏差の値
            sigma = Close.rolling(window=n).std(ddof=0)
            upper_sigma = sma + sigma * deviation
            lower_sigma = sma - sigma * deviation
            #strategy bollingerband
            BuyEntry = ((Low <= lower_sigma) & (Low.shift() > lower_sigma.shift())).values
            SellEntry = ((High >= upper_sigma) & (High.shift() < upper_sigma.shift())).values
            BuyExit = (SellEntry.copy()) #| (Low < lower_sigma2)
            SellExit = (BuyEntry.copy()) #| (High > upper_sigma2)        
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Close":Close, "{}ML".format(n):sma, "TL":upper_sigma, "BL":lower_sigma})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech)

        elif tech == "SAR ":
            #technical SAR
            sar = ind.iSAR(ohlc, 0.002, 0.24) #df,step,acc_maximum
            #strategy 順張り
            BuyEntry = ((Close > sar) & (Close.shift() <= sar.shift())).values
            SellEntry = ((Close < sar) & (Close.shift() >= sar.shift())).values
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Close":Close,  "SAR":sar})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech)

        elif tech == "ICHIMOKU ": 
            #technical ichimoku
            ichimoku = ind.iIchimoku(ohlc, 9, 26, 52)
            tenkan = ichimoku["Tenkan"] 
            kijun = ichimoku["Kijun"]
            senkou1 = ichimoku["SenkouA"]
            senkou2 = ichimoku["SenkouB"]
            chikou = ichimoku["Chikou"]
            #strategy ichimoku
            #kijun vs tenkan
            BuyEntry = ((tenkan > kijun) & (tenkan.shift() <= kijun.shift())).values
            SellEntry = ((tenkan < kijun) & (tenkan.shift() >= kijun.shift())).values
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #chikou vs close
            BuyEntry = ((chikou > Close) & (chikou.shift() <= Close.shift())).values
            SellEntry = ((chikou < Close) & (chikou.shift() >= Close.shift())).values
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #close vs kumo
             BuyEntry = ((Close > senkou1) & (Close.shift() <= senkou1.shift())) &\
        ((Close > senkou2) & (Close.shift() <= senkou2.shift()))
            SellEntry = ((Close < senkou1) & (Close.shift() >= senkou1.shift())) &\
        ((Close < senkou2) & (Close.shift() >= senkou2.shift()))
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Close":Close, "Tenkan":tenkan, "Kijun":kijun})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 

        #Oscillator tech:前にスペース
        elif tech == " MACD":
            #technical MACD
            macd = ind.iMACD(ohlc, 12, 26, 9)
            main = macd["Main"]
            signal = macd["Signal"]
            #strategy MACD
            BuyEntry = ((main > signal) & (main.shift() <= signal.shift())).values
            SellEntry = ((main < signal) & (main.shift() >= signal.shift())).values
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Close":Close, "Main":main, "Signal":signal})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 

        elif tech == " ADX":
            #technical ADX
            adx = ind.iADX(ohlc, 14)
            pdi = adx["PlusDI"]
            mdi = adx["MinusDI"]
            main = adx["Main"]
            #strategy DMI
            BuyEntry = ((pdi > mdi) & (pdi.shift() <= mdi.shift())\
                        & (main > main.shift())).values
            SellEntry = ((pdi < mdi) & (pdi.shift() >= mdi.shift())\
                        & (main < main.shift())).values
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Close":Close, "+DI":pdi, "-DI":mdi, "ADX":main})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 

        elif tech == " RSI":
            #technical RSI
            rsi = ind.iRSI(ohlc, 14)
            #strategy RSI 逆張り
            BuyEntry = ((rsi <= 25) & (rsi.shift() > 25)).values
            SellEntry = ((rsi >= 75) & (rsi.shift() < 75)).values
            BuyExit = ((rsi >= 50) | (rsi <= 15)).values 
            SellExit = ((rsi <= 50) | (rsi >= 85)).values
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"RSI":rsi})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 

        elif tech == " STOCHASTIC":
            #technical stochastic
            sto = ind.iStochastic(ohlc, 5, 3, 3)
            main = sto["Main"]
            signal = sto["Signal"]
            #strategy RSI 逆張り
            BuyEntry = ((main <= 25) & (main.shift() > 25)).values
            SellEntry = ((main >= 75) & (main.shift() < 75)).values
            BuyExit = ((main >= 50) | (main <= 15)).values 
            SellExit = ((main <= 50) | (main >= 85)).values
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Main":main, "Signal":signal})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 

        elif tech == " MOMENTUM":
            #technical momentum
            mom = ind.iMomentum(ohlc, 10)
            #strategy mom
            BuyEntry = ((mom > 100) & (mom.shift() <= 100)).values
            SellEntry = ((mom < 100) & (mom.shift() >= 100)).values
            BuyExit = SellEntry.copy()
            SellExit = BuyEntry.copy()
            #back test
            Trade, PL, HoldPro = bt.Backtest(ohlc, BuyEntry, SellEntry, BuyExit, SellExit, lots, spread)
            Equity = result.BacktestReport(Trade, PL, HoldPro, initial)
            modelchart =  ({"Close":Close, "Momentum":mom})
            modelchart = ch.ModelChart(modelchart, tech)
            #position timing
            long = ch.PositionLine(Trade["Long"])
            short = ch.PositionLine(Trade["Short"])
            position = ch.PositionChart(Open, long, short, tech) 

        else:
            print("Please select technical indicator")
            return

#condition
pip = 0.001
lots = pip * 25
initial = 1000000
spread = 0
diff = pip * 10 #利確、損切り価格差
Strategy(ohlc, lots, initial, spread)#condition