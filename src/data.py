import os
import akshare as ak
import pandas as pd

from dotenv import load_dotenv
from futu import RET_OK, OpenQuoteContext, AuType, KLType
from pandas import DataFrame

from src.util import identify_stock_type, this_year_str, futu_symbol

load_dotenv()


def period_to_kltype(period: str) -> KLType:

    if period == "daily":
        return KLType.K_DAY
    elif period == "weekly":
        return KLType.K_WEEK
    elif period == "monthly":
        return KLType.K_MON
    else:
        raise ValueError("Invalid period: " + period)


def adjust_flag_to_autype(adjust_flag: str) -> AuType:

    if adjust_flag == "qfq":
        return AuType.QFQ
    elif adjust_flag == "hfq":
        return AuType.HFQ
    else:
        raise ValueError("Invalid adjust_flag: " + adjust_flag)


def history_klines_futu(symbol: str,
                        period: str,
                        start_date: str,
                        end_date: str,
                        adjust_flag: str = "qfq") -> DataFrame:
    """获取股票历史K线数据

    Args:
        stock_code (str): 股票代码，如 'HK.00700'
        start_date (str): 开始日期，格式 'YYYY-MM-DD'
        end_date (str): 结束日期，格式 'YYYY-MM-DD'

    Returns:
        pandas.DataFrame: 包含K线数据的DataFrame
    """
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    page_size = 100
    ret_data = pd.DataFrame()
    kl_type = period_to_kltype(period)
    au_type = adjust_flag_to_autype(adjust_flag)

    # 请求第一页数据
    ret, data, page_req_key = quote_ctx.request_history_kline(
        code=futu_symbol(symbol),
        start=start_date,
        end=end_date,
        autype=au_type,
        ktype=kl_type,
        max_count=page_size)
    if ret == RET_OK:
        ret_data = data
    else:
        print('futu 数据查询错误:', data)

    # 请求后续页面的数据
    while page_req_key is not None:
        ret, data, page_req_key = quote_ctx.request_history_kline(
            code=futu_symbol(symbol),
            start=start_date,
            end=end_date,
            autype=au_type,
            ktype=kl_type,
            max_count=page_size,
            page_req_key=page_req_key)
        if ret == RET_OK:
            ret_data = pd.concat([ret_data, data], ignore_index=True)
        else:
            print('futu 数据查询错误:', data)

    quote_ctx.close()

    ret_data.rename(columns={
        'code': '股票代码',
        'name': '股票名称',
        'time_key': '日期',
        'open': '开盘',
        'close': '收盘',
        'high': '最高',
        'low': '最低',
        'volume': '成交量',
        'turnover': '成交额',
        'turnover_rate': '换手率',
        'pe_ratio': '市盈率',
        'change_rate': '涨跌幅',
        'last_close': '昨收',
    }, inplace=True)
    ret_data['日期'] = ret_data['日期'].str.replace(' 00:00:00', '')
    ret_data['涨跌额'] = ret_data['收盘'] - ret_data['开盘']
    return ret_data


def history_klines_akshare(symbol: str,
                           period: str,
                           start_date: str,
                           end_date: str,
                           adjust_flag: str = 'qfq') -> DataFrame:
    """获取历史 K 线

    Args:
        symbol (str): 股票代码
        period (str, optional): K线周期: daily/weekly/monthly. Defaults to 'daily'.
        start_date (str, optional): 开始日期, 格式: yyyymmdd. Defaults to ''.
        end_date (str, optional): 结束日期, 格式: yyyymmdd. Defaults to ''.
        adjust_flag (str, optional): 取值: qfq(前复权), hfq(后复权), 为空则不复权. Defaults to 'qfq'.

    Raises:
        ValueError: 结果为空则会报错

    Returns:
        DataFrame: 返回 df
    """
    stock_type = identify_stock_type(symbol)
    if stock_type == 'A股':
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id21
        klines = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            period=period,
            adjust=adjust_flag)
        klines['成交量'] *= 100

    elif stock_type == 'A股ETF':
        # 参考: https://akshare.akfamily.xyz/data/fund/fund_public.html#id10
        klines = ak.fund_etf_hist_em(
            symbol=symbol,
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            period=period,
            adjust=adjust_flag)
        klines['成交量'] *= 100

    elif stock_type == '港股':
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id66
        klines = ak.stock_hk_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)

    else:
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id56
        klines = ak.stock_us_hist(
            symbol=convert_us_symbol(symbol.upper()),
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)

    if klines.empty:
        raise ValueError("没有数据，请检查参数")
    klines['日期'] = klines['日期'].astype(str)
    klines['股票名称'] = get_stock_name(symbol)
    return klines


def history_klines(symbol: str,
                   period: str,
                   start_date: str,
                   end_date: str,
                   adjust_flag: str = 'qfq') -> DataFrame:
    source = os.environ.get("DATA_SOURCE")

    if source == "akshare":
        data = history_klines_akshare(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust_flag=adjust_flag)
    elif source == "futu":
        data = history_klines_futu(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust_flag=adjust_flag)
    else:
        raise ValueError("请设置环境变量 DATA_SOURCE 为 akshare 或 futu")
    query_info = f'[{source}]查询: [{futu_symbol(symbol)}] {start_date} to {end_date}, {len(data)} rows.'
    print(query_info)
    return data


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
