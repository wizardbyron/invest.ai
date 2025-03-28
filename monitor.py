#!/usr/bin/env python

import fire
import time
from zoneinfo import ZoneInfo

import akshare as ak

from pandas import DataFrame

from src.util.indicators import merge_points
from src.util.tools import is_trading_time
from src.util.strategy import intraday


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
                intraday(points)
        time.sleep(10)
        is_trading = is_trading_time(ZoneInfo(tzone))
    print(f"Market {market} is closed.")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(monitor)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
