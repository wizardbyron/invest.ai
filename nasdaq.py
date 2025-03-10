from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import akshare as ak
from src.util.data import history_klines
from src.util.indicators import pivot_points_index, pivot_points

today = datetime.today()
today_str = today.strftime("%Y%m%d")
start_date = today - timedelta(days=100)
start_date_str = start_date.strftime("%Y%m%d")

# 预读取股票代码
us_symbol_dict = ak.stock_us_spot_em()

df_nasdaq = ak.index_us_stock_sina(symbol=".IXIC")

symbols = ["QQQ", "TQQQ", "SQQQ"]
levels = [1, 5]

for level in levels:
    df = df_nasdaq[-level:]
    points = pivot_points_index(df)
    print(f"{len(df)}日枢轴点:\n{points}\n\n")


for symbol in symbols:
    stock = us_symbol_dict[us_symbol_dict["代码"].str.endswith(f'.{symbol}')]
    print(stock)
    code = stock['代码'].values[0]
    print(code)
    # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id56
    df_daily = ak.stock_us_hist(
        symbol=code,
        period='daily',
        adjust='qfq')

    points = pivot_points(df_daily[-1:])

    output = f"{symbol}:\n{points}\n"

    print(output)

    # df_weekly = history_klines(
    #     type=type,
    #     symbol=symbol,
    #     period='weekly',
    #     start_date=start_date_str,
    #     end_date=today_str)

    # df_monthly = history_klines(
    #     type=type,
    #     symbol=symbol,
    #     period='monthly',
    #     start_date=start_date_str,
    #     end_date=today_str)
