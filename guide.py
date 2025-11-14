#!/usr/bin/env python

import fire
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd

from tabulate import tabulate
from tqdm import tqdm

from src.data import get_stock_name
from src.strategy import pivot_points_grid, ai_guide
from src.util import nowstr, todaystr, format_for_term, get_timezone_by_type, identify_stock_type


def guide(portfolio: str = "all", point_type: str = "斐波那契") -> None:
    """获取交易指南

    Args:
        symbol (str): 代码 or ""
        series (str, optional): 基准价类型：经典/斐波那契/中值. Defaults to "斐波那契".

    Raises:
        ValueError: _description_
    """

    try:
        file = f'./input/portfolios/{portfolio}.csv'
        df_portfolio = pd.read_csv(file, dtype={"代码": str, "名称": str})
        symbols = df_portfolio[["代码", "名称"]].values
    except FileNotFoundError:
        symbols = [
            [str(portfolio).upper(), get_stock_name(str(portfolio))]]

    output_dict = {
        '代码': [],
        '名称': [],
        '当前价格': [],
        '周建议': [],
        '日建议': [],
        'VWAP偏移': [],
    }

    for symbol, name in tqdm(symbols, leave=False):
        time.sleep(1)
        timezone = ZoneInfo(get_timezone_by_type(identify_stock_type(symbol)))
        now = datetime.now(timezone)
        start_date = (now - timedelta(days=15))
        if pd.isna(name):
            name = get_stock_name(symbol)
        resp_weekly = pivot_points_grid(
            symbol=symbol,
            period='weekly',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=now.strftime('%Y-%m-%d'),
            point_type=point_type)
        df_weekly = resp_weekly['merged_table']
        df_weekly.rename_axis('周内交易', inplace=True)
        vwap_weekly = df_weekly.loc['*VWAP>', point_type]

        resp_daily = pivot_points_grid(
            symbol=symbol,
            period='daily',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=now.strftime('%Y-%m-%d'),
            point_type=point_type)
        df_daily = resp_daily['merged_table']
        df_daily.rename_axis('日内交易', inplace=True)
        vwap_daily = df_daily.loc['*VWAP>', point_type]

        output_dict["代码"].append(symbol)
        output_dict["名称"].append(name)
        output_dict["当前价格"].append(resp_weekly['price'])
        output_dict["周建议"].append(format_for_term(resp_weekly['order']))
        output_dict["日建议"].append(format_for_term(resp_daily['order']))
        vwap_diff = (vwap_daily - vwap_weekly)/vwap_weekly
        output_dict["VWAP偏移"].append(f"{vwap_diff:.2%}")

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
