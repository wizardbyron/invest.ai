#!/usr/bin/env python

import fire
import time

import pandas as pd

from tabulate import tabulate
from tqdm import tqdm

from src.data import get_stock_name
from src.strategy import pivot_points_grid
from src.util import nowstr, format_for_term


def guide(portfolio: str = "all", series: str = "参考价") -> None:
    """获取交易指南

    Args:
        symbol (str): 代码 or ""
        series (str, optional): 基准价类型：经典/斐波那契额/参考价. Defaults to "参考价".

    Raises:
        ValueError: _description_
    """

    try:
        file = f'./input/portfolios/{portfolio}.csv'
        df_portfolio = pd.read_csv(file, dtype={"代码": str, "名称": str})
        symbols = df_portfolio[["代码", "名称"]].values
    except FileNotFoundError:
        symbols = [[str(portfolio).upper(), get_stock_name(str(portfolio))]]

    output_dict = {
        '代码': [],
        '名称': [],
        '当前价格': [],
        '周建议': [],
        '日建议': [],
        '均价偏移': [],

    }

    for symbol, name in tqdm(symbols, leave=False):
        if pd.isna(name):
            name = get_stock_name(symbol)
        resp_weekly = pivot_points_grid(symbol, 'weekly', series)
        df_weekly = resp_weekly['merged_table']
        df_weekly.rename_axis('周内交易', inplace=True)
        均价_weekly = df_weekly.loc['*均价>', series]

        resp_daily = pivot_points_grid(symbol, 'daily', series)
        df_daily = resp_daily['merged_table']
        df_daily.rename_axis('日内交易', inplace=True)
        均价_daily = df_daily.loc['*均价>', series]

        output_dict["代码"].append(symbol)
        output_dict["名称"].append(name)
        output_dict["当前价格"].append(resp_weekly['price'])
        output_dict["周建议"].append(format_for_term(resp_weekly['order']))
        output_dict["日建议"].append(format_for_term(resp_daily['order']))
        均价_diff = (均价_daily - 均价_weekly)/均价_weekly
        output_dict["均价偏移"].append(f"{均价_diff:.2%}")

        if len(symbols) == 1:
            weekly_table = tabulate(df_weekly,
                                    headers='keys',
                                    tablefmt="fancy_grid")
            daily_table = tabulate(df_daily,
                                   headers='keys',
                                   tablefmt="fancy_grid")

            weekly_rows = weekly_table.split('\n')
            daily_rows = daily_table.split('\n')

            # 横向拼接行

            combined_rows = [weekly + ' | ' + daily for weekly,
                             daily in zip(weekly_rows, daily_rows)]
            print('\n')
            print('\n'.join(combined_rows))

    print(tabulate(pd.DataFrame(output_dict).set_index('代码'),
                   headers=output_dict.keys(),
                   tablefmt="fancy_grid"))


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")
