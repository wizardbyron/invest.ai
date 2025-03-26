#!/usr/bin/env python

import fire
import time

import akshare as ak

from src.util.indicators import pivot_points


def merge_points(klines):
    points = pivot_points(klines[-2:-1])
    current = klines.iloc[-1]
    points.loc["*最高*"] = current["最高"]
    points.loc["*最低*"] = current["最低"]
    points.loc["*开盘*"] = current["开盘"]
    points.loc["*当前=>"] = current["收盘"]
    close = current["收盘"]
    points["波动率"] = (points["中间值"] - close)/close
    points["波动率"] = points["波动率"].map(lambda x: '{:.2%}'.format(x))
    points = points.sort_values(by="中间值", ascending=False)
    points = points[["中间值", "波动率"]]
    points = points.round(3)
    return points


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
                symbol=symbol,
                period=period)
        else:
            raise ValueError("Invalid market type")

        points = merge_points(klines)
        print(f"{symbol}-{period}\n{klines[-1:]}\n{points}\n")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
