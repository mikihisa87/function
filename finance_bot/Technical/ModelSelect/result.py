import numpy as np
import pandas as pd
from pandas_highcharts.display import display_charts

def BacktestReport(Trade, PL, HoldPro, Initial):
    LongPL = PL['Long']
    LongPLResult = LongPL.sum()
    LongTrades = np.count_nonzero(Trade['Long'])//2
    LongWinTrades = np.count_nonzero(LongPL.clip_lower(0))
    LongLoseTrades = np.count_nonzero(LongPL.clip_upper(0))
    try:
        AveProLong = LongPLResult / LongTrades
    except:
        print("Error")
    
    ShortPL = PL['Short']
    ShortPLResult = ShortPL.sum()
    ShortTrades = np.count_nonzero(Trade['Short'])//2
    ShortWinTrades = np.count_nonzero(ShortPL.clip_lower(0))
    ShortLoseTrades = np.count_nonzero(ShortPL.clip_upper(0))
    try:
        AveProShort = ShortPLResult / ShortTrades
    except:
        print("Error")
        
    Trades = LongTrades + ShortTrades
    WinTrades = LongWinTrades+ShortWinTrades
    LoseTrades = LongLoseTrades+ShortLoseTrades
    AssetChart = (LongPL + ShortPL).cumsum()
    
    GrossProfit = LongPL.clip_lower(0).sum()+ShortPL.clip_lower(0).sum()
    GrossLoss = LongPL.clip_upper(0).sum()+ShortPL.clip_upper(0).sum()
    Profit = GrossProfit+GrossLoss
    AvePro = Profit / Trades
    Equity = (LongPL+ShortPL).cumsum()
    Asset = Initial + Profit
    ROI = (Asset - Initial) / Initial * 100
    MDD = (Equity.cummax()-Equity).max()
    
    vs = HoldPro - Profit
    HoldIni = HoldPro + Initial
    HoldROI = (HoldIni - Initial) / Initial *100
    
    print("Long")
    print('買い数 :', LongTrades)
    print('勝数 :', LongWinTrades)
    print('最大勝 ￥:', LongPL.max())
    try:
        print('平均勝 ￥:', round(LongPL.clip_lower(0).sum()/LongWinTrades, 2))
    except:
        print("Error")
    print('負数 :', LongLoseTrades)
    print('最大負 ￥:', LongPL.min())
    try:
        print('平均負 ￥:', round(LongPL.clip_upper(0).sum()/LongLoseTrades, 2))
    except:
        print("Error")
    print('損益 ￥:', round((LongPLResult), 2))
    print('平均損益 ￥:', round((AveProLong) ,2))
    try:
        print('勝率 :', round(LongWinTrades/LongTrades*100, 2), '%\n')
    except:
        print("Error")
        
    print("Short")
    print('売り数 :', ShortTrades)
    print('勝数 :', ShortWinTrades)
    print('最大勝 ￥:', ShortPL.max())
    try:
        print('平均勝 ￥:', round(ShortPL.clip_lower(0).sum()/ShortWinTrades, 2))
    except:
        print("Error")
    print('負数 :', ShortLoseTrades)
    print('最大負 ￥:', ShortPL.min())
    try:
        print('平均負 ￥:', round(ShortPL.clip_upper(0).sum()/ShortLoseTrades, 2))
    except:
        print("Error")
    print('損益 ￥:', round((ShortPLResult), 2))
    print('平均損益 ￥:', round((AveProShort) ,2))
    try:
        print('勝率 :', round(ShortWinTrades/ShortTrades*100, 2), '%\n')
    except:
        print("Error")

    print("Total")
    print('総数 :', Trades)
    print('総勝数 :', WinTrades)
    print('最大勝 ￥:', max(LongPL.max(), ShortPL.max()))
    try:
        print('平均勝 ￥:', round((LongPL.clip_lower(0).sum()+ShortPL.clip_lower(0).sum())/WinTrades, 2))
    except:
        print("Error")
    print('負数 :', LoseTrades)
    print('最大負 ￥:', min(LongPL.min(), ShortPL.min()))
    try:
        print('平均負 ￥:', round((LongPL.clip_upper(0).sum()+ShortPL.clip_upper(0).sum())/LoseTrades, 2))
    except:
        print("Error")
    print('平均損益 ￥', round(AvePro, 2))
    try:
        print('勝率 :', round(WinTrades/Trades*100, 2), '%\n')
    except:
        print("Error")
    print("結果")
    print('総損益 :', round(Profit, 2))
    print('資産 :￥', Asset)
    print('ROI :', round(ROI, 2),'%')
    print('総利益 :', round(GrossProfit, 2))
    print('総損失 :', round(GrossLoss, 2))
    
    print('\n' '指標')
    try:
        print('Profit Factor :', round(-GrossProfit/GrossLoss, 2))
    except:
        print("Error")
    print('最大ドローダウン :', round(MDD, 2))
    print('Recovery Factor :', round(Profit/MDD, 2))

    print("\n" "Hold Position")
    print("Hold 損益 :￥", round(HoldPro, 2))
    print("Hold 資産 :￥", round(HoldIni, 2))
    print("Hold ROI :", round(HoldROI, 2), '%')
    print("Hold vs Technical :￥", round(vs, 2))
    display_charts(pd.DataFrame({"Assets":AssetChart+Initial}), chart_type="stock",                   title="資産_Chart", figsize=(560,400), grid=True )
    return 