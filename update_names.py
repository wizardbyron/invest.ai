import pandas as pd

from src.data import get_stock_name

full_path = 'input/portfolios/all.csv'
df = pd.read_csv(full_path, dtype={"代码": str, "名称": str})
for index, row in df.iterrows():
    symbol = df.loc[index, "代码"]
    df.loc[index, "名称"] = get_stock_name(symbol)
df = df.sort_values('代码')
df.to_csv(full_path, index=False)
