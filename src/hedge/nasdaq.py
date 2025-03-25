
import datetime

from time import sleep
from zoneinfo import ZoneInfo

import akshare as ak

from src.util.indicators import pivot_points

symbols = ['105.TQQQ', '105.SQQQ']
periods = ['daily']


def is_in_trading_time():
    # 定义开始时间和结束时间
    now = datetime.datetime.now(ZoneInfo('America/New_York'))

    # 判断当前时间是否在指定范围内
    return now.hour in range(9, 16)


def generate_points(klines):
    points = pivot_points(klines[-2:-1])
    today = klines.iloc[-1]
    vwap = today["成交额"].sum() / today["成交量"].sum()
    points.loc["*VWAP"] = vwap
    points.loc["*最高"] = today["最高"]
    points.loc["*开盘"] = today["开盘"]
    points.loc["*最低"] = today["最低"]
    points.loc["*当前>"] = today["收盘"]
    latest = today["收盘"]
    points["波动率"] = (points["中间值"] - latest)/latest
    points["波动率"] = points["波动率"].map(lambda x: '{:.2%}'.format(x))
    points = points.sort_values(by="中间值", ascending=False)
    points = points[["中间值", "波动率"]]
    points = points.round(3)
    return points


while (is_in_trading_time()):
    for symbol in symbols:
        for period in periods:
            klines = ak.stock_us_hist(
                symbol=symbol,
                period=period)
            points = generate_points(klines)
            print(f"{symbol}-{period}\n{points}\n")
    sleep(60)
