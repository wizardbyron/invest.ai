from datetime import datetime

import akshare as ak
import pandas as pd


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

us_symbol_dict = ak.stock_us_spot_em()

df_input = pd.read_csv('selected.csv', dtype={'代码': str})
df_output = df_input.copy()
for index, row in df_input.iterrows():
    print(row)

    type = row['类型']
    symbol = row['代码']
    if type == 'A股':
        history_klines = ak.stock_zh_a_hist(symbol)
    elif type == 'A股ETF':
        history_klines = ak.fund_etf_hist_em(symbol)
    elif type == '港股':
        history_klines = ak.stock_hk_hist(symbol)
    elif type == '美股':
        stock = us_symbol_dict[us_symbol_dict["代码"].str.contains(f'.{symbol}')]
        code = stock['代码'].values[0]
        history_klines = ak.stock_us_hist(code)
    else:
        continue

    # 获取上周的交易数据
    if today.weekday() < 5:  # 交易日
        off_day = today.weekday()
        if history_klines['日期'].iloc[-1] == today.strftime('%Y-%m-%d'):
            off_day += 1  # 当天收盘后，去掉当天数据
        df = history_klines[-level-off_day:-off_day]
    else:  # 周末
        df = history_klines[-level:]

    print(df)

    high = df['最高'].max()
    low = df['最低'].min()
    close = df['收盘'].iloc[-1]

    points = classic(high, low, close)
    df_output.loc[index, f'{level}日阻力位3'] = points['阻力位3']
    df_output.loc[index, f'{level}日阻力位2'] = points['阻力位2']
    df_output.loc[index, f'{level}日阻力位1'] = points['阻力位1']
    df_output.loc[index, f'{level}日枢轴点'] = points['枢轴点']
    df_output.loc[index, f'{level}日支撑位1'] = points['支撑位1']
    df_output.loc[index, f'{level}日支撑位2'] = points['支撑位2']
    df_output.loc[index, f'{level}日支撑位3'] = points['支撑位3']
    df_output.loc[index, f'{level}日预期波动率1(%)'] = points['预期波动率1']
    df_output.loc[index, f'{level}日预期波动率2(%)'] = points['预期波动率2']
    df_output.loc[index, f'{level}日预期波动率3(%)'] = points['预期波动率3']

df_output = df_output.round(3)
df_output.to_csv(f'docs/points/latest.csv', index=False)
df_output.to_csv(f'docs/points/{today_str}.csv', index=False)
