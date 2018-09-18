from pandas_highcharts.display import display_charts
import pandas as pd

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
        if trade[i] == 0 and not Position: Line[i] = 'NaN'
    return Line

def ModelChart(df, tech):
    df = pd.DataFrame(df)
    chart = display_charts(df, title=tech + "_cross", figsize=(560,400), chart_type="stock", grid=True)
    return 

def PositionChart(Open, long, short, tech):
    df = pd.DataFrame(({"Open":Open, "Long":long, "Short":short}))
    position_chart = display_charts(df, title=tech + "_position", figsize=(560,400), chart_type="stock",grid=True)
    return 

