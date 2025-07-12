#!/usr/bin/env python

import fire
import time

import pandas as pd

from src.strategy import pivot_points_grid
from src.util import send_voice, numbers_in_chinese, todaystr


class Guide:
    @classmethod
    def single(cls, symbol: str, series: str = "中间值") -> None:
        """获取价格交易指南

        Args:
            symbol (str): 代码
            series (str, optional): 枢轴点类型：经典/斐波那契额/中间值. Defaults to "中间值".

        Raises:
            ValueError: _description_
        """
        for period in ['weekly', 'daily']:
            pivot_points_grid(symbol, period, series)

    @classmethod
    def portfolio(cls, file: str = "./input/portfolio.csv", series: str = "中间值"):
        """_summary_

        Args:
            data (_type_): _description_
        """

        df_portfolio = pd.read_csv(file, dtype={"代码": str, "名称": str})
        for symbol, name in df_portfolio[["代码", "名称"]].values:
            for period in ['weekly', 'daily']:
                order, price = pivot_points_grid(symbol, period, series)
                if order != "持有":
                    msg = f"注意 {price} 元 {order} 股票 {numbers_in_chinese(name)}"
                    print(f'{period}-{symbol}-{name}:{msg}')


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(Guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时长：{duration/60:.2f}分钟]")
