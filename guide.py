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

us_symbol_dict = ak.stock_us_spot_em()

df_input = pd.read_csv('selected.csv', dtype={'代码': str})
df_output = df_input.copy()
for index, row in df_input.iterrows():
    print(row)

    type = row['类型']
    symbol = row['代码']
    name = row['名称']
    if type == 'A股':
        # https://akshare.akfamily.xyz/data/stock/stock.html#id21
        history_klines = ak.stock_zh_a_hist(symbol)
        market = 'cn'
    elif type == 'A股ETF':
        # https://akshare.akfamily.xyz/data/fund/fund_public.html#id10
        history_klines = ak.fund_etf_hist_em(symbol)
        market = 'cn'
    elif type == '港股':
        # https://akshare.akfamily.xyz/data/stock/stock.html#id66
        history_klines = ak.stock_hk_hist(symbol)
        market = 'hk'
    elif type == '美股':
        stock = us_symbol_dict[us_symbol_dict["代码"].str.endswith(f'.{symbol}')]
        code = stock['代码'].values[0]
        # https://akshare.akfamily.xyz/data/stock/stock.html#id56
        history_klines = ak.stock_us_hist(code)
        market = 'us'
    else:
        continue

    # 获取上周的交易数据
    if today.weekday() < 5 and today.weekday() > 0:  # 交易日
        off_day = today.weekday()
        if history_klines['日期'].iloc[-1] == today.strftime('%Y-%m-%d'):
            off_day += 1  # 当天收盘后，去掉当天数据
        df = history_klines[-level-off_day:-off_day]
    else:  # 周末
        df = history_klines[-level:]

    print(df)

    start_date = df['日期'].iloc[0]
    end_date = df['日期'].iloc[-1]
    high = df['最高'].max()
    low = df['最低'].min()
    close = df['收盘'].iloc[-1]

    c_points = classic(high, low, close)
    f_points = fibonacci(high, low, close)

    item = {'经典': c_points, '斐波那契': f_points}
    row_index = c_points.keys()
    df_single = pd.DataFrame(item, index=row_index)
    df_single['中间值'] = (df_single['经典'] + df_single['斐波那契'])/2
    output_md = f'# {symbol} - {name}\n'
    output_md += f'\n更新日期: {today.strftime('%Y-%m-%d')}\n'
    output_md += f'## 5日枢轴点\n取值日期区间: {start_date} 至 {end_date}\n'
    output_md += f'\n{df_single.round(3).to_markdown()}\n'
    output_md += f'\n## 免责声明\n{disclaimer}\n'

    file_path = f"docs/guide/{market}/{symbol}.md"

    with open(file_path, 'w') as f:
        f.write(output_md)

    df_output.loc[index, f'{level}日经典阻力位3'] = c_points['阻力位3']
    df_output.loc[index, f'{level}日斐波那契阻力位3'] = f_points['阻力位3']
    df_output.loc[index, f'{level}日经典阻力位2'] = c_points['阻力位2']
    df_output.loc[index, f'{level}日斐波那契阻力位2'] = f_points['阻力位2']
    df_output.loc[index, f'{level}日经典阻力位1'] = c_points['阻力位1']
    df_output.loc[index, f'{level}日斐波那契阻力位1'] = f_points['阻力位1']
    df_output.loc[index, f'{level}日枢轴点'] = c_points['枢轴点']
    df_output.loc[index, f'{level}日经典支撑位1'] = c_points['支撑位1']
    df_output.loc[index, f'{level}日斐波那契支撑位1'] = f_points['支撑位1']
    df_output.loc[index, f'{level}日经典支撑位2'] = c_points['支撑位2']
    df_output.loc[index, f'{level}日斐波那契支撑位2'] = f_points['支撑位2']
    df_output.loc[index, f'{level}日经典支撑位3'] = c_points['支撑位3']
    df_output.loc[index, f'{level}日斐波那契支撑位3'] = f_points['支撑位3']
    df_output.loc[index, f'{level}日经典预期波动率1'] = c_points['预期波动率1']
    df_output.loc[index, f'{level}日斐波那契预期波动率1'] = f_points['预期波动率1']
    df_output.loc[index, f'{level}日经典预期波动率2'] = c_points['预期波动率2']
    df_output.loc[index, f'{level}日斐波那契预期波动率2'] = f_points['预期波动率2']
    df_output.loc[index, f'{level}日经典预期波动率3'] = c_points['预期波动率3']
    df_output.loc[index, f'{level}日斐波那契预期波动率3'] = f_points['预期波动率3']

df_output = df_output.round(3)
df_output.to_csv(f'docs/guide/latest.csv', index=False)
df_output.to_csv(f'docs/guide/{today_str}.csv', index=False)
