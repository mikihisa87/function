import requests
a = requests.get("https://www.okex.com/api/v1/future_kline.do?symbol=eth_usd&type=1min&since=15000000000&contract_type=quater&size=3000").json()
len(a)

import psycopg2
import subprocess
import os
import glob
import pandas as pd
import time
from enum import Enum

def get_conn_url():
    url = 'postgresql://{}:{}@{}:5432/{}'.format(
            'crypto',
            'analyzer',
            '199.169.0.99',
            'crypto_analyzer_dev')
    return url

def conn(n_try=5):
    exception = None
    while n_try > 0:
        try:
            return psycopg2.connect(get_conn_url())
        except Exception as e:
            exception = e
            time.sleep(0.5)
            n_try -= 1
    print(exception)

def do_sql(sql):
    c = conn()
    with c.cursor() as cursor:
        try:
            cursor.execute(sql)
            c.commit()
        except Exception as e:
            print(e)

def fetch_all_sql(sql):
    c = conn()
    with c.cursor() as cursor:
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            c.commit()
            return result
        except Exception as e:
            print(e)
            return None

def fetch_one_sql(sql):
    c = conn()
    with c.cursor() as cursor:
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            c.commit()
            return result
        except Exception as e:
            print(e)
            return None

def execute_sql_path(sql_path):
    from crypto_analyzer.config import app_config
    print('\nexecute {}...'.format(os.path.basename(sql_path)))
    db = app_config().DB
    args = db.connect_kwargs
    command = 'psql -h {} -U {} -p 5432 {} < {}'.format(
            args['host'],
            args['user'],
            db.database,
            sql_path)
    print(subprocess.getoutput(command))

def do_migration():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    for sql_path in sorted(glob.glob(os.path.join(dir_name, 'migrations', '*.sql'))):
        execute_sql_path(sql_path)

class Query:
    class Type(Enum):
        INSERT = 'INSERT'
        SELECT_MANY = 'SELECT_MANY'
        SELECT_ONE = 'SELECT_ONE'
        PANDAS = 'PANDAS'

    def __init__(self):
        self.sql = None
        self.mode = 'normal'

    def query(self, query):
        self.sql = query
        return self

    def fetch_mode(self, mode):
        self.mode = mode
        return self

    def run(self):
        if self.sql is None:
            return None

        if self.mode is Query.Type.PANDAS:
            return pd.read_sql_query(self.sql, get_conn_url())
        elif self.mode is Query.Type.SELECT_MANY:
            return fetch_all_sql(self.sql)
        elif self.mode is Query.Type.SELECT_ONE:
            return fetch_one_sql(self.sql)
        elif self.mode is Query.Type.INSERT:
            return do_sql(self.sql)
        else:
            return None

def candlestick_prices(period, currency_code, from_time, to_time, offset, limit,
        desc=False, exchange=None):
    order_by = 'DESC' if desc else ''
    where_exchange = "AND exchange = '{}'".format(exchange) if exchange else ''
    sql = """
    SELECT time_bucket('{}', time) AS period,
    last(last, time) as v_t,
    MAX(last) as v_hi,
    MIN(last) as v_lo,
    last(bid, time) as bid,
    last(ask, time) as ask
    FROM exchange_tickers
    WHERE currency_code = '{}' AND '{}' <= time AND time <= '{}' {}
    GROUP BY period
    ORDER BY period {}
    OFFSET {}
    LIMIT {};
    """.format(period, currency_code, from_time, to_time, where_exchange, order_by, offset, limit)
    return Query().query(sql).fetch_mode(Query.Type.PANDAS).run()

def BTC_csv(candle, path):
    csv = candle.to_csv(path)
    return 

def BTC_df(path):
    df = pd.read_csv(path)
    df.drop(columns={"Unnamed: 0", "bid", "ask"},inplace=True)
    df["Open"] = df["v_t"].shift()
    df.rename(columns={"v_t":"Close", "v_hi":"High", "v_lo":"Low"}, inplace=True) 
    df = df.set_index("period")
    return df