#!/usr/bin/env python

import fire
import time

from src.data import history_klines
from src.indicators import pivot_points_table, merge_points
from src.strategy import pivot_points_grid
from src.util import is_trading_time


def guide(symbol: str) -> None:
    """获取价格交易指南

    Args:
        symbol (str): 代码

    Raises:
        ValueError: _description_
    """
    for period in ['daily', 'weekly']:
        tzone, klines = history_klines(symbol, period)
        if is_trading_time(tzone) and period == 'daily':
            data = klines[-2:-1]
        else:
            data = klines[-1:]
        points = pivot_points_table(data)
        merged_points = merge_points(klines.iloc[-1], points)
        print(f"{symbol}-{period}\n{klines[-1:]}\n{merged_points}")
        pivot_points_grid(merged_points, 1.5, 1.5)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时长：{duration/60:.2f}分钟]")
