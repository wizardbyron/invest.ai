from datetime import datetime

import akshare as ak
import pandas as pd
from utils.pivot_points import classic

level = 5
today = datetime.today()
today_str = today.strftime('%Y%m%d')
offset_days = today.weekday()-1
us_symbol_dict = ak.stock_us_spot_em()

df_input = pd.read_csv('selected.csv', dtype={'代码': str})
df_output = df_input.copy()
for index, row in df_input.iterrows():
    type = row['类型']
    symbol = row['代码']
    if type == 'A股ETF':
        history_klines = ak.fund_etf_hist_em(symbol)
    elif type == '港股':
        history_klines = ak.stock_hk_hist(symbol)
    elif type == '美股':
        stock = us_symbol_dict[us_symbol_dict["代码"].str.contains(f'.{symbol}')]
        code = stock['代码'].values[0]
        history_klines = ak.stock_us_hist(code)
    else:
        continue

    df = history_klines[-offset_days - level: -offset_days]

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
