#!/usr/bin/env python

import fire
import time

import akshare as ak

from src.util.indicators import merge_points
from src.util.strategy import pivot_points_grid
from src.util.tools import is_trading_time, identify_stock_type


def guide(symbol: str):
    """获取价格交易指南

    Args:
        symbol (str): 代码

    Raises:
        ValueError: _description_
    """
    stock_type = identify_stock_type(symbol)
    is_trading = True
    while (is_trading):
        for period in ['daily', 'weekly']:
            # 判断是否为 A 股
            if stock_type == "A股":
                klines = ak.stock_zh_a_hist(
                    symbol=str(symbol),
                    period=period)
            # 判断是否为 A 股 ETF
            elif stock_type == "A股ETF":
                klines = ak.fund_etf_hist_em(
                    symbol=symbol,
                    period=period)
            # 判断是否为港股
            elif stock_type == "港股":
                klines = ak.stock_hk_hist(
                    symbol=symbol,
                    period=period)
            else:
                raise ValueError("不支持的市场或代码")

            if klines.empty:
                raise ValueError("没有数据，请检查参数")

            points = merge_points(klines)
            print(f"{symbol}-{period}\n{klines[-1:]}\n{points}")
            pivot_points_grid(points, 2, 2)
        time.sleep(10)
        is_trading = is_trading_time('Asia/Shanghai')


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时间：{duration:.2f}秒]")
