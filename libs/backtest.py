from datetime import datetime

import akshare as ak
import pandas as pd

from libs.utils.indicators import fibonacci, classic
from libs.utils.data import fetch_klines


def commision(turnover: float) -> float:
    if turnover * 0.0003 < 5.0:
        return 5.0
    else:
        return turnover * 0.0003


def trade_orders(daily_data):
    df_trade_orders = pd.DataFrame(columns=['日期', '方向', '价格'])
    buy_price = 0.0
    sell_price = 0.0
    level = 5
    for index, row in daily_data.iterrows():
        date = row['日期']
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")

        # 获取上周的交易数据计算枢轴点
        if date.weekday() == 0:  # 周一
            df = daily_data[index-level:index]
            # print(df)

            if df.empty:
                continue
            else:
                high = df['最高'].max()
                low = df['最低'].min()
                close = df['收盘'].iloc[-1]

                c_points = classic(high, low, close)
                f_points = fibonacci(high, low, close)

                # buy_price = (c_points['支撑位3'] + f_points['支撑位3'])/2
                # sell_price = (c_points['阻力位3'] + f_points['阻力位3'])/2
                buy_price = f_points['支撑位2']
                sell_price = f_points['阻力位2']

        if row['最低'] <= buy_price and buy_price <= row['最高']:
            order = {
                '日期': date,
                '方向': 'BUY',
                '价格': buy_price
            }
            df_trade_orders.loc[len(df_trade_orders)] = order

        if row['最高'] >= sell_price and sell_price >= row['最低']:
            order = {
                '日期': date,
                '方向': 'SELL',
                '价格': sell_price
            }
            df_trade_orders.loc[len(df_trade_orders)] = order

    df_trade_orders = df_trade_orders.round(3)

    return df_trade_orders


def backtest():
    today = datetime.today()
    today_str = today.strftime('%Y%m%d')
    start_date = '20200101'
    end_date = today_str

    us_symbol_dict = ak.stock_us_spot_em()
    df_input = pd.read_csv('input/backtest.csv', dtype={'代码': str})
    df_output = df_input.copy()

    for idx, row in df_input.iterrows():
        # print(row)

        type = row['类型']
        symbol = row['代码']
        name = row['名称']
        market, daily_data = fetch_klines(
            type=type,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            adjust_flag='qfq')

        if market == None:
            continue

        df_trade_orders = trade_orders(daily_data)
        df_trade_orders.to_csv(f'output/{name}_orders.csv', index=False)

        init = 100000
        trade_unit = 10000
        hold = 0
        balance = init
        trade_times = 0
        df_trade_roi = df_trade_orders.copy()

        for index, row in df_trade_orders.iterrows():
            type = row['方向']
            price = row['价格']

            if type == 'BUY' and trade_unit * price < balance:
                hold += trade_unit
                balance -= trade_unit * price
                fee = commision(trade_unit * price)
                balance -= fee
                df_trade_roi.loc[index, '交易数量'] = trade_unit
                df_trade_roi.loc[index, '持有数量'] = hold
                df_trade_roi.loc[index, '成交额'] = -trade_unit * price
                df_trade_roi.loc[index, '手续费'] = fee
                df_trade_roi.loc[index, '余额'] = balance
                trade_times += 1

            if type == 'SELL' and hold > 0:
                hold -= trade_unit
                balance += trade_unit * price
                fee = commision(trade_unit * price)
                balance -= fee
                df_trade_roi.loc[index, '交易数量'] = -trade_unit
                df_trade_roi.loc[index, '持有数量'] = hold
                df_trade_roi.loc[index, '成交额'] = trade_unit * price
                df_trade_roi.loc[index, '手续费'] = fee
                df_trade_roi.loc[index, '余额'] = balance
                trade_times += 1

        df_trade_roi = df_trade_roi.round(2)
        df_trade_roi = df_trade_roi[df_trade_roi['成交额'].abs() > 0.0]
        df_trade_roi.to_csv(f'output/{name}_trade.csv', index=False)

        df_output.loc[idx, '账户余额'] = balance
        df_output.loc[idx, '持仓数量'] = hold
        df_output.loc[idx, '起始价格'] = daily_data['收盘'].iloc[0]
        df_output.loc[idx, '最新价格'] = daily_data['收盘'].iloc[-1]
        df_output.loc[idx, '持仓市值'] = daily_data['收盘'].iloc[-1] * hold
        df_output.loc[idx, '合计'] = daily_data['收盘'].iloc[-1] * hold + balance
        trade_roi = (daily_data['收盘'].iloc[-1] * hold + balance - init)/init
        df_output.loc[idx, '交易收益率'] = trade_roi

        start_close = daily_data['收盘'].iloc[0]
        end_close = daily_data['收盘'].iloc[-1]
        non_trade_roi = (end_close - start_close) / start_close

        df_output.loc[idx, '自然收益率'] = non_trade_roi
        df_output.loc[idx, '超额收益率'] = trade_roi - non_trade_roi
        df_output.loc[idx, '交易次数'] = trade_times

    df_output = df_output.round(3)
    df_output = df_output.sort_values(by='超额收益率', ascending=False)

    df_output['交易收益率'] = df_output['交易收益率'].apply(lambda x: "{:.2%}".format(x))
    df_output['自然收益率'] = df_output['自然收益率'].apply(lambda x: "{:.2%}".format(x))
    df_output['超额收益率'] = df_output['超额收益率'].apply(lambda x: "{:.2%}".format(x))

    print(df_output)
    df_output.to_csv(f'output/backtest_roi_{start_date}.csv', index=False)
