#!/usr/bin/env python

import fire
import time

import akshare as ak

from src.util.indicators import merge_points
from src.util.strategy import pivot_points_grid


def guide(market: str, symbol: str):
    """获取价格交易指南

    Args:
        market (str): a, etf, hk
        symbol (str): 代码

    Raises:
        ValueError: _description_
    """

    for period in ['daily', 'weekly']:
        if market == "etf":
            klines = ak.fund_etf_hist_em(
                symbol=symbol,
                period=period)
        elif market == "hk":
            klines = ak.stock_hk_hist(
                symbol=symbol,
                period=period)
        elif market == "a":
            klines = ak.stock_zh_a_hist(
                symbol=str(symbol),
                period=period)
        else:
            raise ValueError("Invalid market type")

        points = merge_points(klines)
        print(f"{symbol}-{period}\n{klines[-1:]}\n{points}\n")
        pivot_points_grid(points)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时间：{duration:.2f}秒]")
