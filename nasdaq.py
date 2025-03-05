import akshare as ak
from src.util.indicators import pivot_points_index

df_nasdaq = ak.index_us_stock_sina(symbol=".IXIC")

levels = [1, 5]

for level in levels:
    df = df_nasdaq[-level:]
    points = pivot_points_index(df)
    print(df)
    print(f"{level}日枢轴点:\n{points}\n\n")
