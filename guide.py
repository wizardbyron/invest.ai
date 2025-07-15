#!/usr/bin/env python

import fire
import time

import pandas as pd

from src.strategy import pivot_points_grid
from src.util import numbers_in_chinese


def guide(symbol: str = "", period: str = "", series: str = "中间值") -> None:
    """获取价格交易指南

    Args:
        symbol (str): 代码 or ""
        series (str, optional): 枢轴点类型：经典/斐波那契额/中间值. Defaults to "中间值".

    Raises:
        ValueError: _description_
    """

    if symbol == "":
        file = "./input/portfolio.csv"
        df_portfolio = pd.read_csv(file, dtype={"代码": str, "名称": str})
        symbols = df_portfolio[["代码", "名称"]].values
    else:
        symbols = [[symbol, symbol]]

    if period == "":
        periods = ['weekly', 'daily']
    else:
        periods = [period]

    orders = []
    for symbol, name in symbols:
        for period in periods:
            msg, price = pivot_points_grid(symbol, period, series)
            if msg.find("观望") == -1:
                print(f'{period}-{symbol}-{name}:{msg}')
                orders.append(msg)

    if len(orders) > 0:
        print("\n交易建议如下:")
        for order in orders:
            print(order)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时长：{duration:.2f}秒]")
