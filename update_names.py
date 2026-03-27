import pandas as pd
from futu import RET_OK, OpenQuoteContext

from src.util import futu_symbol


def get_stock_name(symbol: str) -> str | None:
    """从 futu-api 获取港股/美股名称

    Args:
        symbol (str): 股票代码

    Returns:
        str | None: 股票名称，获取失败返回 None
    """
    quote_ctx = OpenQuoteContext(host="127.0.0.1", port=11111)
    try:
        futu_code = futu_symbol(symbol)
        ret, data = quote_ctx.get_market_snapshot([futu_code])
        if ret == RET_OK and not data.empty:
            return data.iloc[0]["name"]
    except:
        pass
    finally:
        quote_ctx.close()
    return None


full_path = "input/portfolios/all.csv"
df = pd.read_csv(full_path, dtype={"代码": str, "名称": str})
for index, row in df.iterrows():
    symbol = df.loc[index, "代码"]
    name = get_stock_name(symbol)
    if name:
        df.loc[index, "名称"] = name
df = df.sort_values("代码")
df.to_csv(full_path, index=False)
