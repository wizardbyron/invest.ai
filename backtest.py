import fire
import time

import pandas as pd

from src.strategy import pivot_points_table
from src.data import history_klines
from src.util import nowstr


series_enum = {
    'fibo': '斐波那契',
    'classic': '经典',
    'mid': '中值'
}


def weekly_daily_points(symbol: str, start_date_str: str, end_date_str: str, series_param: str) -> None:
    symbol = str(symbol)
    cache_file = f'.cache/backtest_{symbol}_{start_date_str}_{end_date_str}.csv'

    try:
        df_all = pd.read_csv(cache_file)
    except FileNotFoundError:
        daily_data = history_klines(
            symbol=symbol,
            period='daily',
            start_date=str(start_date_str),
            end_date=str(end_date_str),
            adjust_flag='qfq')
        daily_data['type'] = 'daily'

        weekly_data = history_klines(
            symbol=symbol,
            period='weekly',
            start_date=str(start_date_str),
            end_date=str(end_date_str),
            adjust_flag='qfq')
        weekly_data['type'] = 'weekly'

        df_all = pd.concat([daily_data, weekly_data], ignore_index=True)
        df_all = df_all.sort_values(by=['日期'], ascending=True)
        df_all.to_csv(cache_file, index=False)

    series = series_enum[series_param]
    weekly_points = None
    trades = []
    stop_loss_price = 0.0
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
            today = row

            daily_points = pivot_points_table(prev_day)
            daily_guide = {
                'prev_day': prev_day,
                'points': daily_points,
            }

            low = today['最低']
            high = today['最高']

            weekly_pos = 2.0
            weekly_buy_price = weekly_points.loc[f'支撑位{weekly_pos:.1f}', series]
            weekly_sell_price = weekly_points.loc[f'阻力位{weekly_pos:.1f}', series]

            daily_pos = 1.5
            daily_buy_price = daily_points.loc[f'支撑位{daily_pos:.1f}', series]
            daily_sell_price = daily_points.loc[f'阻力位{daily_pos:.1f}', series]
            if low <= weekly_buy_price and low <= daily_buy_price:
                trades.append({
                    '指令': '买入',
                    '买入价': daily_buy_price,
                    '当日': today,
                    '周指南': weekly_guide,
                    '日指南': daily_guide,
                })
                stop_loss_price = weekly_points.loc[f'支撑位3.0', series]
                last_buy_date = today['日期']

            if low <= stop_loss_price:
                if today['日期'] != last_buy_date:
                    trades.append({
                        '指令': '止损',
                        '卖出价': stop_loss_price,
                        '当日': today
                    })
                    stop_loss_price = 0.0

            if high >= weekly_sell_price and high >= daily_sell_price:
                trades.append({
                    '指令': '卖出',
                    '卖出价': daily_sell_price,
                    '当日': today,
                    '周指南': weekly_guide,
                    '日指南': daily_guide,
                })
    return df_all, trades


def weekly_points(symbol: str, start_date_str: str, end_date_str: str, series_param: str) -> None:
    symbol = str(symbol)
    cache_file = f'.cache/backtest_weekly_{symbol}_{start_date_str}_{end_date_str}.csv'

    try:
        df_all = pd.read_csv(cache_file)
    except FileNotFoundError:
        daily_data = history_klines(
            symbol=symbol,
            period='daily',
            start_date=str(start_date_str),
            end_date=str(end_date_str),
            adjust_flag='qfq')
        daily_data['type'] = 'daily'

        weekly_data = history_klines(
            symbol=symbol,
            period='weekly',
            start_date=str(start_date_str),
            end_date=str(end_date_str),
            adjust_flag='qfq')
        weekly_data['type'] = 'weekly'

        df_all = pd.concat([daily_data, weekly_data], ignore_index=True)
        df_all = df_all.sort_values(by=['日期'], ascending=True)
        df_all.to_csv(cache_file, index=False)

    series = series_enum[series_param]
    weekly_points = None
    trades = []
    stop_loss_point = 3.0
    stop_loss_price = 0.0
    weekly_pos = 2.0
    for idx, row in df_all.iterrows():
        if row['type'] == 'weekly':
            prev_week = df_all.iloc[idx:idx+1]
            weekly_points = pivot_points_table(prev_week)
            weekly_guide = {
                'prev_week': prev_week,
                'points': weekly_points,
            }
        else:
            if weekly_points is None or idx == 0:
                continue

            today = row

            low = today['最低']
            high = today['最高']

            weekly_buy_price = weekly_points.loc[f'支撑位{weekly_pos:.1f}', series]
            weekly_sell_price = weekly_points.loc[f'阻力位{weekly_pos:.1f}', series]

            if low <= weekly_buy_price:
                trades.append({
                    '指令': '买入',
                    '买入价': weekly_buy_price,
                    '当日': today,
                    '周指南': weekly_guide,
                })
                stop_loss_price = weekly_points.loc[f'支撑位{stop_loss_point:.1f}', series]
                last_buy_date = today['日期']

            if low <= stop_loss_price:
                if today['日期'] != last_buy_date:
                    trades.append({
                        '指令': '止损',
                        '卖出价': stop_loss_price,
                        '当日': today
                    })
                    stop_loss_price = 0.0

            if high >= weekly_sell_price:
                trades.append({
                    '指令': '卖出',
                    '卖出价': weekly_sell_price,
                    '当日': today,
                    '周指南': weekly_guide,
                })
    return df_all, trades


def daily_points(symbol: str, start_date_str: str, end_date_str: str, series_param: str) -> None:
    symbol = str(symbol)
    cache_file = f'.cache/backtest_daily_{symbol}_{start_date_str}_{end_date_str}.csv'

    try:
        df_all = pd.read_csv(cache_file)
    except FileNotFoundError:
        df_all = history_klines(
            symbol=symbol,
            period='daily',
            start_date=str(start_date_str),
            end_date=str(end_date_str),
            adjust_flag='qfq')

    series = series_enum[series_param]
    trades = []
    for idx, row in df_all.iterrows():
        if idx == 0:
            continue

        prev_day = df_all.iloc[idx-1:idx]
        today = row

        daily_points = pivot_points_table(prev_day)
        daily_guide = {
            'prev_day': prev_day,
            'points': daily_points,
        }

        low = today['最低']
        high = today['最高']

        daily_pos = 2.0
        daily_buy_price = daily_points.loc[f'支撑位{daily_pos:.1f}', series]
        daily_sell_price = daily_points.loc[f'阻力位{daily_pos:.1f}', series]

        if low <= daily_buy_price:
            trades.append({
                '指令': '买入',
                '买入价': daily_buy_price,
                '当日': today,
                '日指南': daily_guide,
            })

        if high >= daily_sell_price:
            trades.append({
                '指令': '卖出',
                '卖出价': daily_sell_price,
                '当日': today,
                '日指南': daily_guide,
            })
    return df_all, trades


def all_in(df_all, trades):
    init = 100000
    hold = 0
    balance = init
    last_buy_price = 0
    trade_times = 0

    for item in trades:

        if item['指令'] == '买入' and balance > 0:
            amount = balance/item['买入价']-balance/item['买入价'] % 100
            balance -= amount * item['买入价']
            hold += amount
            last_buy_price = item["买入价"]
            trade_times += 1
            print(
                f'日期:{item['当日']['日期']}, 买入价格:{last_buy_price:.3f}, 买入数量：{amount}，买入金额:{hold*item["买入价"]:.2f}, 余额：{balance:.2f}')

        if item['指令'] == '卖出' and hold > 0 and item['卖出价'] > last_buy_price:
            balance += hold * item['卖出价']
            print(
                f'日期:{item['当日']['日期']}, 卖出价格:{item['卖出价']:.3f}, 卖出数量：{hold}，卖出金额:{hold*item["卖出价"]:.2f}, 余额：{balance:.2f}')
            hold = 0
            trade_times += 1
            last_buy_price = 0

        if item['指令'] == '止损':
            balance += hold * item['卖出价']
            trade_times += 1
            print(
                f'日期:{item['当日']['日期']}, 卖出价格:{item['卖出价']:.3f}, 持仓数量：{hold}，卖出金额:{amount*item["卖出价"]:.2f}, 余额：{balance:.2f}(止损)')
            hold = 0

    value = balance + hold * df_all.iloc[-1]['收盘']
    trade_roi = ((value) / init) - 1
    base_roi = (df_all.iloc[-1]['收盘'] / df_all.iloc[0]['收盘']) - 1

    print(f'初始资金：{init:.2f}, 期末持仓：{hold}, 期末余额：{balance:.2f}, 期末市值：{value:.2f}')
    print(f'交易收益率：{trade_roi:.2%}, 基准收益率：{base_roi:.2%}')
    print(f'收益率差:{trade_roi - base_roi:.2%}，交易次数：{trade_times}')
    return trade_roi


def run_backtest(symbol: str, start_date: str, end_date: str) -> dict[str, float]:
    result = {}
    for series in ['classic', 'fibo', 'mid']:
        print('='*40)
        print(f'策略：{series}')
        df_all, trades = weekly_points(symbol, start_date, end_date, series)
        # df_all, trades = daily_points(symbol, start_date, end_date, series)
        result['series'] = all_in(df_all, trades)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(run_backtest)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")
