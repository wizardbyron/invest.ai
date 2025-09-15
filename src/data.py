from datetime import datetime

import akshare as ak
import pandas as pd
from pandas import DataFrame


from src.util import identify_stock_type, this_year_str, todaystr


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
        klines['成交量'] *= 100
        tzone = 'Asia/Shanghai'

    elif stock_type == 'A股ETF':
        # 参考: https://akshare.akfamily.xyz/data/fund/fund_public.html#id10
        klines = ak.fund_etf_hist_em(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)
        klines['成交量'] *= 100
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
            symbol=convert_us_symbol(symbol.upper()),
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
    df_symbol_cache = f".cache/us_symbols.csv"
    try:
        df_symbols = pd.read_csv(df_symbol_cache)
    except Exception as e:
        df_symbols = ak.stock_us_spot_em()
        df_symbols.to_csv(df_symbol_cache, index=False)
    stock = df_symbols[df_symbols["代码"].str.endswith(f'.{symbol}')]
    return stock['代码'].values[0]


def cn_bond(term: str = '10y',  year: str = this_year_str()) -> DataFrame:
    """中国国债收益率（官方）

    Args:
        term (str, optional): 期限. Defaults to '10y'.
        year (str, optional): 年份. Defaults to this_year_str().

    Returns:
        _type_: _description_
    """
    url = f'https://yield.chinabond.com.cn/cbweb-mn/yc/downYearBzqx?year={year}&&wrjxCBFlag=0&&zblx=txy&&ycDefId=2c9081e50a2f9606010a3068cae70001&&locale=zh_CN'
    df = pd.read_excel(url)
    return df[df['标准期限说明'] == term]


def us_bond(term: str = '10 Yr',  year: str = this_year_str()) -> DataFrame:
    """美国国债收益率（美国财政部）

    Args:
        term (str, optional): 国债期限. Defaults to '10 Yr'.
        year (str, optional): _description_. Defaults to this_year_str().
        recent_days (int, optional): _description_. Defaults to 30.

    Returns:
        _type_: _description_
    """
    url = f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?field_tdr_date_value={year}&type=daily_treasury_yield_curve&page&_format=csv"
    df = pd.read_csv(url)
    return df[["Date", term]]


def get_stock_name(symbol: str) -> str:
    """获取股票名称

    Args:
        symbol (str): 股票代码

    Returns:
        str: 股票名称
    """

    stock_type = identify_stock_type(symbol)
    if stock_type == 'A股':
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id8
        name = ak.stock_individual_info_em(symbol).loc[2]['value']
    elif stock_type == 'A股ETF':
        # 参考: https://akshare.akfamily.xyz/data/fund/fund_public.html#id1
        df_symbol_cache = f".cache/zh_etf_symbols.csv"
        try:
            df_symbols = pd.read_csv(df_symbol_cache, dtype={"基金代码": str})
        except FileNotFoundError as e:
            df_symbols = ak.fund_name_em()
            df_symbols.to_csv(df_symbol_cache, index=False)
        name = df_symbols[df_symbols['基金代码'] == symbol]['基金简称'].values[0]
    elif stock_type == '港股':
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id65
        df_symbol_cache = f".cache/hk_symbols.csv"
        try:
            df_symbols = pd.read_csv(df_symbol_cache, dtype={'代码': str})
        except FileNotFoundError as e:
            df_symbols = ak.stock_hk_spot_em()
            df_symbols.to_csv(df_symbol_cache, index=False)
        name = df_symbols[df_symbols['代码'] == symbol]['名称'].values[0]
    else:  # 美股
        df_symbol_cache = f".cache/us_symbols.csv"
        try:
            df_symbols = pd.read_csv(df_symbol_cache)
        except FileNotFoundError as e:
            df_symbols = ak.stock_us_spot_em()
            df_symbols.to_csv(df_symbol_cache, index=False)
        stock = df_symbols[df_symbols["代码"].str.endswith(f'.{symbol.upper()}')]
        name = stock['名称'].values[0]

    return name
