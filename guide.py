#!/usr/bin/env python

import fire
import time

import pandas as pd

from src.data import history_klines
from src.indicators import pivot_points_table, merge_points
from src.strategy import pivot_points_grid
from src.util import in_trading_time, send_voice, numbers_in_chinese


buy_points = {
    "weekly": 2.0,
    "daily": 1.5
}

sell_points = {
    "weekly": 2.0,
    "daily": 1.5
}


class Guide:
    @classmethod
    def guide(cls, symbol: str, series: str = "中间值") -> None:
        """获取价格交易指南

        Args:
            symbol (str): 代码
            series (str, optional): 枢轴点类型：经典/斐波那契额/中间值. Defaults to "中间值".

        Raises:
            ValueError: _description_
        """
        for period in ['weekly', 'daily']:
            tzone, klines = history_klines(str(symbol), period)
            if not in_trading_time(tzone) and period == 'daily':
                data = klines[-1:]  # 非交易时间 daily 只取最新一条数据
            else:
                data = klines[-2:-1]
            points = pivot_points_table(data)
            merged_points = merge_points(klines.iloc[-1], points, series)
            print(f"\n{symbol}-{period}:\n{klines[-1:]}\n{merged_points}")
            pivot_points_grid(
                merged_points,
                sell_points[period],
                buy_points[period],
                series)

    @classmethod
    def watch(cls, symbol: str, series: str = "中间值") -> None:
        """检测价格，发送交易通知

        Args:
            symbol (str): 代码
            series (str, optional): 枢轴点类型：经典/斐波那契额/中间值. Defaults to "中间值".

        Raises:
            ValueError: _description_
        """
        is_in_trading_time = True
        while is_in_trading_time:
            for period in ['weekly', 'daily']:
                tzone, klines = history_klines(str(symbol), period)
                is_in_trading_time = in_trading_time(tzone)
                data = klines[-2:-1]
                points = pivot_points_table(data)
                merged_points = merge_points(klines.iloc[-1], points, series)
                print(f"\n{symbol}-{period}:\n{klines[-1:]}\n{merged_points}")
                order, price = pivot_points_grid(
                    merged_points,
                    sell_points[period],
                    buy_points[period],
                    series)
                if order != "持有":
                    msg = f"注意 {price} 元 {order} 股票 {numbers_in_chinese(symbol)}"
                    send_voice(msg)

            time.sleep(10)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(Guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时长：{duration/60:.2f}分钟]")
