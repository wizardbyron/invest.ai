import os

import pandas as pd

from src.data import get_stock_name

path = "./input/portfolios"
dir = os.listdir(path)

for file in dir:
    if file.endswith(".csv"):
        full_path = os.path.join(path, file)
        df = pd.read_csv(full_path, dtype={"代码": str, "名称": str})
        for index, row in df.iterrows():
            symbol = df.loc[index, "代码"]
            df.loc[index, "名称"] = get_stock_name(symbol)
        df.to_csv(full_path, index=False)
