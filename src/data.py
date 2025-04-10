from datetime import datetime

import akshare as ak
import pandas as pd
from pandas import DataFrame

from src.util import identify_stock_type


def history_klines(symbol: str,
                   period: str,
                   start_date: str = "19700101",
                   end_date: str = "22220101",
                   adjust_flag: str = 'qfq') -> tuple[str, DataFrame]:
    """获取历史 K 线

    Args:
        type (str): 类型: A股/A股ETF/港股/美股
        symbol (str): 股票代码
        period (str, optional): K线周期: daily/weekly/monthly. Defaults to 'daily'.
        start_date (str, optional): 开始日期, 格式: yyyymmdd. Defaults to ''.
        end_date (str, optional): 结束日期, 格式: yyyymmdd. Defaults to ''.
        adjust_flag (str, optional): 取值: qfq(前复权), hfq(后复权), 为空则不复权. Defaults to 'qfq'.

    Raises:
        ValueError: 结果为空则会报错

    Returns:
        str: 时区
        DataFrame: 返回 df
    """
    stock_type = identify_stock_type(symbol)
    if stock_type == 'A股':
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id21
        klines = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)
        tzone = 'Asia/Shanghai'

    elif stock_type == 'A股ETF':
        # 参考: https://akshare.akfamily.xyz/data/fund/fund_public.html#id10
        klines = ak.fund_etf_hist_em(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)
        tzone = 'Asia/Shanghai'

    elif stock_type == '港股':
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id66
        klines = ak.stock_hk_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)
        tzone = 'Hongkong'

    else:
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id56
        klines = ak.stock_us_hist(
            symbol=convert_us_symbol(symbol),
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)
        tzone = 'America/New_York'

    if klines.empty:
        raise ValueError("没有数据，请检查参数")
    klines['日期'] = klines['日期'].astype(str)
    return tzone, klines


def convert_us_symbol(symbol: str) -> str:
    """美股代码转换

    Args:
        symbol (str): 美股代码

    Returns:
        str: 美股代码（带市场标记）
    """
    today_str = datetime.now().strftime("%Y%m%d")
    df_symbol_cache = f".cache/us_symbols{today_str}.csv"
    try:
        df_symbols = pd.read_csv(df_symbol_cache)
    except Exception as e:
        df_symbols = ak.stock_us_spot_em()
        df_symbols.to_csv(df_symbol_cache, index=False)
    stock = df_symbols[df_symbols["代码"].str.endswith(f'.{symbol}')]
    return stock['代码'].values[0]
