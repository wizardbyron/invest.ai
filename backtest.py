from datetime import datetime
import fire
import time

import pandas as pd
from pandas import DataFrame

from src.indicators import fibonacci, classic
from src.strategy import pivot_points_table
from src.data import history_klines
from src.util import nowstr


def commision(turnover: float) -> float:
    if turnover * 0.0003 < 5.0:
        return 5.0
    else:
        return turnover * 0.0003


series_enum = {
    'fibo': '斐波那契',
    'classic': '经典',
    'mid': '参考价'
}


def run_backtest(symbol: str, start_date_str: str, end_date_str: str = '22220101', series_param: str = 'mid') -> None:
    symbol = str(symbol)
    cache_file = f'.cache/backtest_{symbol}_{start_date_str}.csv'

    try:
        df_all = pd.read_csv(cache_file)
    except FileNotFoundError:
        tz, daily_data = history_klines(
            symbol=symbol,
            period='daily',
            start_date=str(start_date_str),
            end_date=str(end_date_str),
            adjust_flag='qfq')
        daily_data['type'] = 'daily'

        tz, weekly_data = history_klines(
            symbol=symbol,
            period='weekly',
            start_date=str(start_date_str),
            end_date=str(end_date_str),
            adjust_flag='qfq')
        weekly_data['type'] = 'weekly'

        df_all = pd.concat([daily_data, weekly_data], ignore_index=True).sort_values(
            by=['日期'], ascending=True)
        df_all.to_csv(cache_file, index=False)

    series = series_enum[series_param]
    weekly_points = None
    trades = []
    # print(df_all)
    for idx, row in df_all.iterrows():
        if row['type'] == 'weekly':
            prev_week = df_all.iloc[idx:idx+1]
            weekly_points = pivot_points_table(prev_week)
            weekly_guide = {
                'prev_week': prev_week,
                'points': weekly_points,
            }
        else:
            if weekly_points is None:
                continue
            if df_all.loc[idx-1, 'type'] == 'weekly':
                prev_day = df_all.iloc[idx-2:idx-1]
            else:
                prev_day = df_all.iloc[idx-1:idx]

            daily_points = pivot_points_table(prev_day)
            daily_guide = {
                'prev_day': df_all.iloc[idx:idx+1],
                'points': daily_points,
            }

            low = df_all.iloc[idx]['最低']
            high = df_all.iloc[idx]['最高']

            weekly_pos = 2.0
            weekly_buy_price = weekly_points.loc[f'支撑位{weekly_pos:.1f}', series]
            weekly_sell_price = weekly_points.loc[f'阻力位{weekly_pos:.1f}', series]

            # daily_pos = 1.5
            # daily_buy_price = daily_points.loc[f'支撑位{daily_pos:.1f}', series]
            # daily_sell_price = daily_points.loc[f'阻力位{daily_pos:.1f}', series]
            if low <= weekly_buy_price:
                trades.append({
                    '指令': '买入',
                    '买入价': weekly_buy_price,
                    '当日': row,
                    '周指南': weekly_guide,
                    '日指南': daily_guide,
                })

            if high >= weekly_sell_price:
                trades.append({
                    '指令': '卖出',
                    '卖出价': weekly_sell_price,
                    '当日': row,
                    '周指南': weekly_guide,
                    '日指南': daily_guide,
                })

    # trades = []
    init = 100000
    # trade_unit = 100
    hold = 0
    balance = init
    last_buy_price = 0

    for item in trades:
        # print(item)
        if item['指令'] == '买入' and balance > 0:
            amount = balance/item['买入价']-balance/item['买入价'] % 100
            balance -= amount * item['买入价']
            hold += amount
            last_buy_price = item["买入价"]
            print(
                f'日期:{item['当日']['日期']}, 买入价格:{last_buy_price:.3f}, 买入数量：{amount}，买入金额:{hold*item["买入价"]:.2f}, 余额：{balance:.2f}')

        if item['指令'] == '卖出' and hold > 0 and item['卖出价'] > last_buy_price:
            balance += hold * item['卖出价']
            print(
                f'日期:{item['当日']['日期']}, 卖出价格:{item['卖出价']:.3f}, 卖出数量：{hold}，卖出金额:{hold*item["卖出价"]:.2f}, 余额：{balance:.2f}')
            hold = 0
            # last_buy_price = 0

    print(
        f'期末持仓：{hold}，期末余额：{balance:.2f}, 期末市值：{balance + hold * df_all.iloc[-1]['收盘']:.2f}')

    print(
        f'初始资金：{init:.2f},收益率：{((balance + hold * df_all.iloc[-1]['收盘']) / init) - 1:.2%}')

    print(f'基准收益率：{df_all.iloc[-1]["收盘"] / df_all.iloc[0]["收盘"] - 1:.2%}')


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(run_backtest)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")
