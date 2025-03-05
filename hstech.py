import akshare as ak
from src.util.indicators import pivot_points_index

df_hstech = ak.stock_hk_index_daily_sina(symbol="HSTECH")

levels = [1, 5]

for level in levels:
    df = df_hstech[-level-2:-2]
    points = pivot_points_index(df)
    print(df)
    print(f"{level}日枢轴点:\n{points}\n\n")
