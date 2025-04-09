#!/usr/bin/env python

import fire
import time

import akshare as ak
from pandas import DataFrame

from src.util.indicators import pivot_points_table, merge_points
from src.util.strategy import pivot_points_grid
from src.util.tools import is_trading_time, identify_stock_type

us_symbols = ak.stock_us_spot_em()


def history_klines(symbol: str, period: str) -> tuple[str, DataFrame]:
    """获取A股/港股历史K线数据

    Args:
        symbol (str): 股票代码
        period (str): 周期（daily/weekly/monthly）

    Raises:
        ValueError: _description_
        ValueError: _description_

    Returns:
        DataFrame: 历史 K 线数据
    """

    stock_type = identify_stock_type(symbol)
    if stock_type == "A股":
        klines = ak.stock_zh_a_hist(
            symbol=str(symbol),
            period=period)
        tzone = 'Asia/Shanghai'
    elif stock_type == "A股ETF":
        klines = ak.fund_etf_hist_em(
            symbol=symbol,
            period=period)
        tzone = 'Asia/Shanghai'
    elif stock_type == "港股":
        klines = ak.stock_hk_hist(
            symbol=symbol,
            period=period)
        tzone = 'Hongkong'
    else:
        stock = us_symbols[us_symbols["代码"].str.endswith(f'.{symbol}')]
        code = stock['代码'].values[0]
        klines = ak.stock_us_hist(
            symbol=code,
            period=period,
            adjust='qfq')
        tzone = 'America/New_York'

    if klines.empty:
        raise ValueError("没有数据，请检查参数")
    return tzone, klines


def guide(symbol: str) -> None:
    """获取价格交易指南

    Args:
        symbol (str): 代码

    Raises:
        ValueError: _description_
    """
    is_trading = True
    while (is_trading):
        for period in ['daily', 'weekly']:
            tzone, klines = history_klines(symbol, period)
            points = pivot_points_table(klines[-2:-1])
            merged_points = merge_points(klines.iloc[-1], points)
            print(f"{symbol}-{period}\n{klines[-1:]}\n{merged_points}")
            pivot_points_grid(merged_points, 2, 2)
        time.sleep(10)
        is_trading = is_trading_time(tzone)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时长：{duration/60:.2f}分钟]")
