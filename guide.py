#!/usr/bin/env python

import fire
import time

import pandas as pd

from tabulate import tabulate

from src.strategy import pivot_points_grid
from src.util import nowstr, format_for_term


def guide(symbol: str = "", series: str = "中间值") -> None:
    """获取交易指南

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
        symbols = [[str(symbol), str(symbol)]]

    output_dict = {
        '代码': [],
        '名称': [],
        '当前价格': [],
        '周建议': [],
        '日建议': [],

    }

    for symbol, name in symbols:
        weekly = pivot_points_grid(symbol, 'weekly', series)
        daily = pivot_points_grid(symbol, 'daily', series)
        output_dict["代码"].append(symbol)
        output_dict["名称"].append(name)
        output_dict["当前价格"].append(weekly['price'])
        output_dict["周建议"].append(format_for_term(weekly['order']))
        output_dict["日建议"].append(format_for_term(daily['order']))

        if len(symbols) == 1:
            table_weekly = tabulate(weekly['merged_table'],
                                    headers="keys",
                                    tablefmt="fancy_grid")
            table_daily = tabulate(daily['merged_table'],
                                   headers="keys",
                                   tablefmt="fancy_grid")
            print(f'{symbol}-{name}\nWeekly:\n{table_weekly}\nDaily:\n{table_daily}')

    print(tabulate(pd.DataFrame(output_dict).set_index('代码'),
                   headers=['代码', '名称', '当前价格', '周建议', '日建议'],
                   tablefmt="fancy_grid"))


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")
