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


def fetch_kline(symbol: str, start_date: str, end_date: str, type: str):
    if type == 'A股':
        # https://akshare.akfamily.xyz/data/stock/stock.html#id21
        history_klines = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period='daily')
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
        history_klines = ak.stock_hk_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period='daily')
        market = 'hk'
    elif type == '美股':
        stock = us_symbol_dict[us_symbol_dict["代码"].str.endswith(f'.{symbol}')]
        code = stock['代码'].values[0]
        # https://akshare.akfamily.xyz/data/stock/stock.html#id56
        history_klines = ak.stock_us_hist(
            symbol=code,
            start_date=start_date,
            end_date=end_date,
            period='daily')
        market = 'us'
    else:
        market = None
        history_klines = None

    return market, history_klines


today = datetime.today()
today_str = today.strftime('%Y%m%d')
start_date = '20240101'
end_date = today_str

us_symbol_dict = ak.stock_us_spot_em()
df_input = pd.read_csv('backtest.csv', dtype={'代码': str})
df_output = df_input.copy()

for idx, row in df_input.iterrows():
    print(row)

    type = row['类型']
    symbol = row['代码']
    name = row['名称']
    market, daily_data = fetch_kline(
        type=type,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date)

    if market == None:
        continue

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

                # print(df_single.round(3))
                buy_price = (c_points['支撑位1'] + c_points['支撑位1'])/2
                sell_price = (c_points['阻力位1'] + c_points['阻力位1'])/2

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
    df_trade_orders.to_csv(f'output/{name}_orders.csv', index=False)

    init = 100000
    hold = 0
    balance = init
    trade_unit = 10000
    df_trade_roi = df_trade_orders.copy()
    for index, row in df_trade_orders.iterrows():
        type = row['方向']
        price = row['价格']

        if type == 'BUY' and trade_unit * price < balance:
            hold += trade_unit
            balance -= trade_unit * price
            df_trade_roi.loc[index, '交易数量'] = trade_unit
            df_trade_roi.loc[index, '持有数量'] = hold
            df_trade_roi.loc[index, '成交额'] = -trade_unit * price
            df_trade_roi.loc[index, '余额'] = balance

        if type == 'SELL' and hold > 0:
            hold -= trade_unit
            balance += trade_unit * price
            df_trade_roi.loc[index, '交易数量'] = -trade_unit
            df_trade_roi.loc[index, '持有数量'] = hold
            df_trade_roi.loc[index, '成交额'] = trade_unit * price
            df_trade_roi.loc[index, '余额'] = balance

    df_trade_roi = df_trade_roi.round(2)
    df_trade_roi = df_trade_roi[df_trade_roi['成交额'].abs() > 0.0]
    df_trade_roi.to_csv(f'output/{name}_trade.csv', index=False)

    df_output.loc[idx, '账户余额'] = balance
    df_output.loc[idx, '持仓数量'] = hold
    df_output.loc[idx, '最新价格'] = daily_data['收盘'].iloc[-1]
    df_output.loc[idx, '持仓市值'] = daily_data['收盘'].iloc[-1] * hold
    df_output.loc[idx, '合计'] = daily_data['收盘'].iloc[-1] * hold + balance
    trade_roi = (daily_data['收盘'].iloc[-1] * hold + balance - init)/init * 100
    df_output.loc[idx, '交易收益率'] = f'{trade_roi:.2f}%'

    non_trade_roi = (daily_data['收盘'].iloc[-1] -
                     daily_data['收盘'].iloc[0])/daily_data['收盘'].iloc[0] * 100
    df_output.loc[idx, '自然收益率'] = f'{non_trade_roi:.2f}%'
    df_output.loc[idx, '超额收益率'] = f'{trade_roi - non_trade_roi:.2f}%'

df_output = df_output.round(3)
df_output.to_csv(f'回报率测算.csv', index=False)
print(df_output)
