#!/usr/bin/env python

import fire
import time

import pandas as pd

from src.data import get_points
from src.strategy import pivot_points_grid
from src.util import send_voice, numbers_in_chinese, todaystr


p_sell = {
    "weekly": 2.0,
    "daily": 1.5
}

p_buy = {
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
            points = get_points(symbol, series, period)
            pivot_points_grid(points, p_buy[period], p_sell[period], series)

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
                points = get_points(symbol, series, period)
                order, price = pivot_points_grid(
                    points, p_buy[period], p_sell[period], series)
                if order != "持有":
                    msg = f"注意 {price} 元 {order} 股票 {numbers_in_chinese(str(symbol))}"
                    send_voice(msg)
            time.sleep(10)

    @classmethod
    def portfolio_guide(cls, file: str = "./input/portfolio.csv", series: str = "中间值"):
        """_summary_

        Args:
            data (_type_): _description_
        """

        df_portfolio = pd.read_csv(file, dtype={"代码": str})
        for period in ['weekly', 'daily']:
            file_name = f"./output/guides/{todaystr()}_{period}.xlsx"
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                for symbol, name in df_portfolio[["代码", "名称"]].values:
                    print(f'{period}-{symbol}')
                    points = get_points(symbol, series, period)
                    order, price = pivot_points_grid(
                        points,
                        p_buy[period],
                        p_sell[period],
                        series)
                    sheet_name = f'{symbol}-{name}'
                    points.to_excel(writer, sheet_name=sheet_name)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(Guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时长：{duration/60:.2f}分钟]")
