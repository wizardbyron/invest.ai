#!/usr/bin/env python

import fire
import time
from zoneinfo import ZoneInfo

import akshare as ak

from pandas import DataFrame

from src.util.indicators import merge_points
from src.util.tools import is_trading_time


def trade(points: DataFrame):
    cur_price = points.loc["*当前>", "中间值"]
    if points.loc["*开盘", "中间值"] > points.loc["*昨收", "中间值"]:  # 高开
        buy_point = "支撑位1.5"
        sell_point = "阻力位1.5"
    else:  # 低开
        buy_point = "支撑位1.5"
        sell_point = "阻力位1.5"
    buy_price = points.loc[buy_point, "中间值"]
    sell_price = points.loc[sell_point, "中间值"]
    if cur_price > sell_price:
        print(f"当前价格{cur_price}高于{sell_price}，建议卖出")
    elif cur_price < buy_price:
        print(f"当前价格{cur_price}低于{buy_price}，建议买入")
    else:
        print(f"当前价格{cur_price}在{buy_price}和{sell_price}之间，观望")


def monitor(market: str):
    symbol_map = {
        'qqq': {
            'symbols': ['105.TQQQ', '105.SQQQ'],
            'time_zone': 'America/New_York',
        },
        'yy': {
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
    is_trading = True
    while (is_trading):
        for symbol in symbols:
            for period in ['daily', 'weekly']:
                if market in ["qqq", "yy"]:
                    klines = ak.stock_us_hist(
                        symbol=symbol,
                        period=period)
                elif market == "hstech":
                    klines = ak.stock_hk_hist(
                        symbol=symbol,
                        period=period)
                points = merge_points(klines)
                print(f"{symbol}-{period}\n{points}\n")
                trade(points)
        time.sleep(10)
        is_trading = is_trading_time(ZoneInfo(tzone))
    print(f"Market {market} is closed.")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(monitor)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
