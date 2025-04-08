#!/usr/bin/env python

import fire
import time

import akshare as ak

from src.util.tools import is_trading_time
from src.util.indicators import pivot_points_table, merge_points
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
                period='daily',
                adjust='qfq')
            points = pivot_points_table(klines[-2:-1])
            merged_points = merge_points(klines.iloc[-1], points)
            print(f"{symbol}\n{merged_points}\n")
            pivot_points_grid(merged_points)
        time.sleep(5)
        is_trading = is_trading_time('America/New_York')
    print(f"Market is closed.")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(watch)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时长：{duration/60:.2f}分钟]")
