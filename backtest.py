from datetime import datetime

import akshare as ak
import pandas as pd

disclaimer = '本站用于实验目的，不构成任何投资建议，也不作为任何法律法规、监管政策的依据，\
    投资者不应以该等信息作为决策依据或依赖该等信息做出法律行为，由此造成的一切后果由投资者自行承担。'


def classic(high: float, low: float, close: float) -> dict[str, float]:
    """
    计算经典支撑位和阻力位
    :param high: 最高价
    :param low: 最低价
    :param close: 收盘价
    :return: 经典支撑位和阻力位
    """
    p = (high + low + close)/3

    s1 = 2 * p - high
    s2 = p - (high - low)
    s3 = low - 2 * (high - p)

    r1 = 2 * p - low
    r2 = p + (high - low)
    r3 = high + 2 * (p - low)

    return {
        "阻力位3": r3,
        "阻力位2": r2,
        "阻力位1": r1,
        "枢轴点": p,
        "支撑位1": s1,
        "支撑位2": s2,
        "支撑位3": s3,
        "预期波动率1": (r1-s1)/p * 100,
        "预期波动率2": (r2-s2)/p * 100,
        "预期波动率3": (r3-s3)/p * 100
    }


def fibonacci(high: float, low: float, close: float) -> dict[str, float]:
    """
    计算斐波那契支撑位和阻力位
    :param high: 最高价
    :param low: 最低价
    :param close: 收盘价
    :return: 斐波那契支撑位和阻力位
    """
    p = (high + low + close)/3
    s1 = p - (high - low) * 0.382
    s2 = p - (high - low) * 0.618
    s3 = p - (high - low)
    r1 = p + (high - low) * 0.382
    r2 = p + (high - low) * 0.618
    r3 = p + (high - low)

    return {
        "阻力位3": r3,
        "阻力位2": r2,
        "阻力位1": r1,
        "枢轴点": p,
        "支撑位1": s1,
        "支撑位2": s2,
        "支撑位3": s3,
        "预期波动率1": (r1-s1)/p * 100,
        "预期波动率2": (r2-s2)/p * 100,
        "预期波动率3": (r3-s3)/p * 100
    }


level = 5
today = datetime.today()
today_str = today.strftime('%Y%m%d')
start_date = '20240101'
end_date = '20241231'

us_symbol_dict = ak.stock_us_spot_em()

df_input = pd.read_csv('backtest.csv', dtype={'代码': str})
df_output = df_input.copy()
for idx, row in df_input.iterrows():
    print(row)

    type = row['类型']
    symbol = row['代码']
    name = row['名称']
    if type == 'A股':
        # https://akshare.akfamily.xyz/data/stock/stock.html#id21
        history_klines = ak.stock_zh_a_hist(
            symbol, start_date=start_date, end_date=end_date)
        market = 'cn'
    elif type == 'A股ETF':
        # https://akshare.akfamily.xyz/data/fund/fund_public.html#id10
        history_klines = ak.fund_etf_hist_em(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period='daily')
        market = 'cn'
    elif type == '港股':
        # https://akshare.akfamily.xyz/data/stock/stock.html#id66
        history_klines = ak.stock_hk_hist(symbol, start_date, end_date)
        market = 'hk'
    elif type == '美股':
        stock = us_symbol_dict[us_symbol_dict["代码"].str.endswith(f'.{symbol}')]
        code = stock['代码'].values[0]
        # https://akshare.akfamily.xyz/data/stock/stock.html#id56
        history_klines = ak.stock_us_hist(code, start_date, end_date)
        market = 'us'
    else:
        continue

    # print(history_klines)
    buy_price = 0.0
    sell_price = 0.0
    df_trade_orders = pd.DataFrame(
        columns=['日期', '方向', '价格', '数量', '持仓', '成交额', '剩余资金'])
    hold = 0
    init = 100000
    for index, row in history_klines.iterrows():
        date_str = row['日期']
        date = datetime.strptime(date_str, "%Y-%m-%d")

        # 获取上周的交易数据计算枢轴点
        if date.weekday() == 0:  # 周一
            off_day = date.weekday()
            df = history_klines[index-5:index]
            # print(df)

            if df.empty:
                continue
            else:
                high = df['最高'].max()
                low = df['最低'].min()
                close = df['收盘'].iloc[-1]

                c_points = classic(high, low, close)
                f_points = fibonacci(high, low, close)

                item = {'经典': c_points, '斐波那契': f_points}
                row_index = c_points.keys()
                df_single = pd.DataFrame(item, index=row_index)
                df_single['中间值'] = (df_single['经典'] + df_single['斐波那契'])/2

                # print(df_single)
                buy_price = c_points['支撑位2']
                sell_price = c_points['阻力位2']

        if row['最低'] <= buy_price and init > buy_price * 10000:
            hold += 10000
            init += buy_price * -10000
            order = {
                '日期': date_str,
                '方向': 'BUY',
                '价格': buy_price,
                '数量': 10000,
                '持仓': hold,
                '成交额': buy_price * -10000,
                '剩余资金': init
            }
            df_trade_orders.loc[len(df_trade_orders)] = order
        if row['最高'] >= sell_price and hold >= 10000:
            hold -= 10000
            init += sell_price * 10000
            order = {
                '日期': date_str,
                '方向': 'SELL',
                '价格': sell_price,
                '数量': -10000,
                '持仓': hold,
                '成交额': sell_price * 10000,
                '剩余资金': init
            }
            df_trade_orders.loc[len(df_trade_orders)] = order

    df_trade_orders.to_excel(f'{name}_orders.xlsx')
    total_profit = df_trade_orders['成交额'].sum()
    hold_num = df_trade_orders['持仓'].iloc[-1]
    hold_value = history_klines['收盘'].iloc[-1] * hold_num
    roi = (init+hold_value-100000.00)/100000.00*100
    print(f'剩余资金: {init:.2f}, 持有市值:{hold_value:.2f}, 收益率:{roi:.2f}% \n')
    df_output.loc[idx, '剩余资金'] = init
    df_output.loc[idx, '持有市值'] = hold_value
    df_output.loc[idx, '收益率'] = roi

df_output = df_output.round(3)
df_output.to_csv('roi.csv', index=False)
roi_avg = df_output['收益率'].mean()
print(f'平均收益率:{roi_avg:.2f}\n')
