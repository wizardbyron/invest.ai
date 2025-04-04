#!/usr/bin/env python

import fire
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import akshare as ak

from src.util.tools import is_trading_time
from src.util.indicators import merge_points
from src.util.strategy import pivot_points_grid


def watch(key: str):
    hedge_map = {
        'qqq': ['105.TQQQ', '105.SQQQ'],
        'vix': ['107.VIXY', '107.SVIX'],
        'fix': ['107.YINN', '107.YANG'],
    }
    is_trading = True
    while (is_trading):
        for symbol in hedge_map[key]:
            klines = ak.stock_us_hist(
                symbol=symbol,
                period='weekly',
                adjust='qfq')
            points = merge_points(klines)
            print(f"{symbol}\n{points}\n")
            pivot_points_grid(points)
        time.sleep(10)
        is_trading = is_trading_time('America/New_York')
    print(f"Market is closed.")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(watch)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
