#!/usr/bin/env python

import fire
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import akshare as ak

from src.util.indicators import merge_points
from src.util.strategy import intraday


def is_trading_time():
    # 美股交易时间通常是从早上9:30到下午4:00（纽约时间）
    ny_tz = ZoneInfo('America/New_York')
    now_ny = datetime.now(ny_tz)
    market_open = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)

    # 检查是否在交易日
    if now_ny.weekday() in range(0, 5):  # 0-4 表示周一到周五
        return market_open <= now_ny <= market_close
    return False


def watch(code: str):
    # 预读取股票代码
    us_symbol_dict = ak.stock_us_spot_em()
    stock = us_symbol_dict[us_symbol_dict["代码"].str.endswith(f'.{code}')]
    symbol = stock['代码'].values[0]

    is_trading = True
    while (is_trading):
        for period in ['daily', 'weekly']:
            klines = ak.stock_us_hist(
                symbol=symbol,
                period=period)
            points = merge_points(klines)
            print(f"{symbol}-{period}\n{points}\n")
            intraday(points)
        time.sleep(10)
        is_trading = is_trading_time()
    print(f"Market is closed.")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(watch)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
