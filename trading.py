#!/sbin/env python

import fire
import time
from zoneinfo import ZoneInfo

import akshare as ak

from src.util.indicators import pivot_points
from src.util.tools import is_in_trading_time


def merge_points(klines):
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


class Trading():
    def monitor(self, market: str):
        symbol_map = {
            'nasdaq': {
                'symbols': ['105.TQQQ', '105.SQQQ'],
                'time_zone': 'America/New_York',
            },
            'yinnyang': {
                'symbols': ['107.YINN', '107.YANG'],
                'time_zone': 'America/New_York',
            },
            'hstech': {
                'symbols': ['07226', '07552'],
                'time_zone': 'Hongkong',
            }
        }
        tzone = symbol_map[market]['time_zone']
        symbols = symbol_map[market]['symbols']
        while (is_in_trading_time(ZoneInfo(tzone))):
            for symbol in symbols:
                for period in ['daily', 'weekly']:
                    if market in ["nasdaq", "yinnyang"]:
                        klines = ak.stock_us_hist(
                            symbol=symbol,
                            period=period)
                    elif market == "hstech":
                        klines = ak.stock_hk_hist(
                            symbol=symbol,
                            period=period)
                        points = merge_points(klines)
                        print(f"{symbol}-{period}\n{points}\n")
            time.sleep(10)
        print(f"Market {market} is closed.")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(Trading)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
