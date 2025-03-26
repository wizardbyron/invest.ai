#!/usr/bin/env python

import fire
import time
from zoneinfo import ZoneInfo

import akshare as ak

from src.util.indicators import pivot_points
from src.util.tools import is_in_trading_time


def merge_points(klines):
    points = pivot_points(klines[-2:-1])
    last = klines.iloc[-1]
    points.loc["*最高*"] = last["最高"]
    points.loc["*最低*"] = last["最低"]
    points.loc["*开盘*"] = last["开盘"]
    points.loc["*当前=>"] = last["收盘"]
    latest = last["收盘"]
    points["波动率"] = (points["中间值"] - latest)/latest
    points["波动率"] = points["波动率"].map(lambda x: '{:.2%}'.format(x))
    points = points.sort_values(by="中间值", ascending=False)
    points = points[["中间值", "波动率"]]
    points = points.round(3)
    return points


def guide_etf(symbol: str):
    for period in ['weekly']:
        klines = ak.fund_etf_hist_em(
            symbol=symbol,
            period=period)
        points = merge_points(klines)
        print(f"{symbol}-{period}\n{klines[-1:]}\n{points}\n")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide_etf)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
