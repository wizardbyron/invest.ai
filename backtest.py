#!/usr/bin/env python
from datetime import datetime, timedelta
import os
import fire
import time

import pandas as pd

from src.strategy import pivot_points_table
from src.data import history_klines
from src.util import nowstr


def find_weekline_index(df, given_date):
    """
    找到给定日期在DataFrame中比它早的最近一个日期的行索引。

    :param df: Pandas DataFrame，包含日期列
    :param date_column: 日期列的列名
    :param given_date: 给定的日期，应为Pandas的Timestamp类型或可转换为该类型的对象
    :return: 比给定日期早的最近一个日期的行索引
    """
    # 确保给定日期是Timestamp类型
    given_date = pd.to_datetime(given_date)

    # 找到所有小于给定日期的行
    mask = df['日期'] < given_date

    # 如果没有小于给定日期的行，返回None
    if not mask.any():
        return None

    # 找到比给定日期早的最近一个日期的行索引
    return df.loc[mask, '日期'].idxmax()


def weekly_grid(symbol: str, start_date_str: str, end_date_str: str, point_type: str) -> None:
    symbol = str(symbol)

    daily_klines = history_klines(
        symbol=symbol,
        period='daily',
        start_date=str(start_date_str),
        end_date=str(end_date_str))

    end_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    weekly_start_date = end_date - timedelta(days=15)
    weekly_klines = history_klines(
        symbol=symbol,
        period='weekly',
        start_date=weekly_start_date.strftime('%Y-%m-%d'),
        end_date=str(end_date_str))

    weekly_klines['日期'] = pd.to_datetime(
        weekly_klines['日期'], format='%Y-%m-%d')

    weekly_pos = 2.0
    stop_loss_point = 3.0
    stop_loss_price = 0.0

    df_order = daily_klines.copy()
    df_order['指令'] = '观望'

    for idx, today in df_order.iterrows():

        latest_weekly_index = find_weekline_index(weekly_klines, today['日期'])
        weekly_lines = weekly_klines[latest_weekly_index-1:latest_weekly_index]

        weekly_points = pivot_points_table(weekly_lines)[point_type]

        buy_price = weekly_points.loc[f'支撑位{weekly_pos:.1f}']
        sell_price = weekly_points.loc[f'阻力位{weekly_pos:.1f}']

        df_order.loc[idx, '参考周线日期'] = weekly_lines.iloc[0]['日期']

        df_order.loc[idx, '买入价'] = buy_price
        df_order.loc[idx, '卖出价'] = sell_price
        df_order.loc[idx, '止损价'] = stop_loss_price

        if today['最低'] <= buy_price:
            df_order.loc[idx, '指令'] = '买入'
            df_order.loc[idx, '买入价'] = buy_price
            stop_loss_price = weekly_points.loc[f'支撑位{stop_loss_point:.1f}']
            last_buy_date = today['日期']

        if today['最低'] <= stop_loss_price and today['日期'] != last_buy_date:  # 避免当天交易
            df_order.loc[idx, '指令'] = '止损'
            df_order.loc[idx, '卖出价'] = stop_loss_price
            stop_loss_price = 0.0

        if today['最高'] >= sell_price:
            df_order.loc[idx, '指令'] = '卖出'
            df_order.loc[idx, '卖出价'] = sell_price
            stop_loss_price = 0.0

    filename = f'output/weekly_grid_{symbol}_{point_type}_{start_date_str.replace("-", "")}_{end_date_str.replace("-", "")}.csv'
    df_order.to_csv(filename, index=False)
    return daily_klines, df_order


def daily_grid(symbol: str, start_date_str: str, end_date_str: str, point_type: str) -> None:
    symbol = str(symbol)

    daily_klines = history_klines(
        symbol=symbol,
        period='daily',
        start_date=str(start_date_str),
        end_date=str(end_date_str))

    daily_pos = 1.5
    stop_loss_point = 2.0
    stop_loss_price = 0.0

    df_order = daily_klines.copy()
    df_order['指令'] = '观望'

    for idx, today in df_order.iterrows():
        if idx == 0:
            continue

        daily_points = pivot_points_table(daily_klines[idx-1:idx])[point_type]

        buy_price = daily_points.loc[f'支撑位{daily_pos:.1f}']
        sell_price = daily_points.loc[f'阻力位{daily_pos:.1f}']

        df_order.loc[idx, '买入价'] = buy_price
        df_order.loc[idx, '卖出价'] = sell_price
        df_order.loc[idx, '止损价'] = stop_loss_price

        if today['最低'] <= buy_price:
            df_order.loc[idx, '指令'] = '买入'
            df_order.loc[idx, '买入价'] = buy_price
            stop_loss_price = daily_points.loc[f'支撑位{stop_loss_point:.1f}']
            last_buy_date = today['日期']

        if today['最低'] <= stop_loss_price and today['日期'] != last_buy_date:  # 避免当天交易
            df_order.loc[idx, '指令'] = '止损'
            df_order.loc[idx, '卖出价'] = stop_loss_price
            stop_loss_price = 0.0

        if today['最高'] >= sell_price:
            df_order.loc[idx, '指令'] = '卖出'
            df_order.loc[idx, '卖出价'] = sell_price
            stop_loss_price = 0.0

    filename = f'output/weekly_grid_{symbol}_{point_type}_{start_date_str.replace("-", "")}_{end_date_str.replace("-", "")}.csv'
    df_order.to_csv(filename, index=False)
    return daily_klines, df_order


def all_in_trade(df_all, df_order):
    init = 100000  # 初始资金
    hold = 0  # 持仓
    balance = init  # 余额
    last_buy_price = 0  # 上次买入价格
    last_buy_turnover = 0  # 上次买入额，用于计算利润
    trade_times = 0  # 交易次数
    stop_loss_times = 0  # 止损次数
    df_trade = df_order.copy()

    for idx, order in df_trade.iterrows():

        if order['指令'] == '买入' and balance > 0:
            volume = balance/order['买入价']-balance/order['买入价'] % 100
            turnover = volume * order['买入价']
            balance -= turnover
            hold += volume
            last_buy_price = order["买入价"]
            if volume > 0:
                last_buy_turnover = turnover
            trade_times += 1

            df_trade.loc[idx, '交易-成交量'] = volume
            df_trade.loc[idx, '持仓量'] = hold
            df_trade.loc[idx, '交易-成交额'] = turnover
            df_trade.loc[idx, '余额'] = balance

        if order['指令'] == '卖出' and hold > 0 and order['卖出价'] > last_buy_price:
            volume = hold
            turnover = volume * order['卖出价']
            hold = 0
            balance += turnover
            trade_times += 1
            last_buy_price = 0

            df_trade.loc[idx, '交易-成交量'] = volume
            df_trade.loc[idx, '持仓量'] = hold
            df_trade.loc[idx, '交易-成交额'] = turnover
            df_trade.loc[idx, '余额'] = balance
            df_trade.loc[idx, '利润'] = turnover - last_buy_turnover

            last_buy_turnover = 0

        if order['指令'] == '止损':
            volume = hold
            turnover = volume * order['卖出价']
            balance += turnover
            last_buy_price = 0
            hold = 0
            # loss = turnover - last_buy_turnover

            stop_loss_times += 1
            trade_times += 1

            df_trade.loc[idx, '交易-成交量'] = volume
            df_trade.loc[idx, '持仓量'] = hold
            df_trade.loc[idx, '交易-成交额'] = turnover
            df_trade.loc[idx, '余额'] = balance
            df_trade.loc[idx, '利润'] = turnover - last_buy_turnover
            last_buy_turnover = 0

    df_trade.set_index('日期', inplace=True)
    symbol = df_all['股票代码'].iloc[0]
    start_date = df_all['日期'].iloc[0].replace('-', '')
    end_date = df_all['日期'].iloc[-1].replace('-', '')
    file = f'output/trade_all_in_{symbol}_{start_date}_{end_date}.csv'
    df_trade.to_csv(file)

    value = balance + hold * df_all.iloc[-1]['收盘']
    trade_roi = ((value) / init) - 1
    base_roi = (df_all.iloc[-1]['收盘'] / df_all.iloc[0]['收盘']) - 1

    print(f'初始资金：{init:.2f}, 期末持仓：{hold}, 期末余额：{balance:.2f}, 期末市值：{value:.2f}')
    print(f'交易收益率：{trade_roi:.2%}, 基准收益率：{base_roi:.2%}')
    print(
        f'超额收益率:{trade_roi - base_roi:.2%}，交易次数：{trade_times}, 止损次数:{stop_loss_times}')
    return {
        '测试记录': df_trade,
        '交易收益率': f"{trade_roi:.2%}",
        '基准收益率': f"{base_roi:.2%}",
        '超额收益率': f"{trade_roi - base_roi:.2%}",
        '交易次数': trade_times,
        '止损次数': stop_loss_times
    }


class Backtest:
    @classmethod
    def individual(clz, symbol: str, start_date: str, end_date: str) -> dict[str, float]:
        result = {}
        for point_type in ['经典', '斐波那契', '中值']:
            print('='*40)
            # print(f'策略：{point_type}')
            df_all, df_orders = weekly_grid(
                symbol, start_date, end_date, point_type)
            result[point_type] = all_in_trade(df_all, df_orders)
        # print(f'策略:{point_type}，超额收益率: {result[point_type]['超额收益率']}')
        # return result

    @classmethod
    def portfolio(cls, file_name: str, start_date: str, end_date: str):
        full_path = f'input/portfolios/{file_name}.csv'
        df = pd.read_csv(full_path, dtype={"代码": str, "名称": str})
        df_output = df.copy()
        for index, row in df_output.iterrows():
            symbol = df_output.loc[index, "代码"]
            result = cls.individual(symbol, start_date, end_date)
            df_output.loc[index, "基准收益率"] = result['经典']['基准收益率']
            df_output.loc[index, "经典-交易收益率"] = result['经典']['交易收益率']
            df_output.loc[index, "经典-超额收益率"] = result['经典']['超额收益率']
            df_output.loc[index, "经典-交易次数"] = result['经典']['交易次数']
            df_output.loc[index, "经典-止损次数"] = result['经典']['止损次数']
            df_output.loc[index, "斐波那契-交易收益率"] = result['斐波那契']['交易收益率']
            df_output.loc[index, "斐波那契-超额收益率"] = result['斐波那契']['超额收益率']
            df_output.loc[index, "斐波那契-交易次数"] = result['斐波那契']['交易次数']
            df_output.loc[index, "斐波那契-止损次数"] = result['斐波那契']['止损次数']
            df_output.loc[index, "中值-交易收益率"] = result['中值']['交易收益率']
            df_output.loc[index, "中值-超额收益率"] = result['中值']['超额收益率']
            df_output.loc[index, "中值-交易次数"] = result['中值']['交易次数']
            df_output.loc[index, "中值-止损次数"] = result['中值']['止损次数']
            time.sleep(1)
        df_output['开始日期'] = start_date
        df_output['结束日期'] = end_date
        # print(df_output)
        output_filename = f'output/backtest_{file_name}_{start_date.replace("-", "")}_{end_date.replace("-", "")}.csv'
        df_output.to_csv(output_filename, index=False)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(Backtest)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")
