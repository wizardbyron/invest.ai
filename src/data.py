import pandas as pd
from dotenv import load_dotenv
from futu import RET_OK, OpenQuoteContext, AuType, KLType
from pandas import DataFrame

from src.util import this_year_str, futu_symbol

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


def history_klines_futu(
        symbol: str,
        period: str,
        start_date: str,
        end_date: str,
        adjust_flag: str = "qfq") -> DataFrame:

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
    if ret_data.empty:
        raise ValueError("没有数据，请检查参数")
    ret_data['日期'] = ret_data['日期'].str.replace(' 00:00:00', '')
    ret_data['涨跌额'] = ret_data['收盘'] - ret_data['开盘']
    return ret_data


def history_klines(
        symbol: str,
        period: str,
        start_date: str,
        end_date: str,
        adjust_flag: str = 'qfq') -> DataFrame:

    data = history_klines_futu(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust_flag=adjust_flag)

    query_info = f'[futu]查询[{futu_symbol(symbol)}], 类型: {period},{start_date} to {end_date}, {len(data)} rows.'
    print(query_info)
    return data


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
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    try:
        futu_code = futu_symbol(symbol)
        market = futu_code.split('.')[0]
        for stock_type in ('STOCK', 'ETF'):
            ret, data = quote_ctx.get_stock_basicinfo(market=market, stock_type=stock_type)
            if ret == RET_OK:
                row = data[data['code'] == futu_code]
                if not row.empty:
                    return row['name'].values[0]
        raise ValueError(f"futu 无法获取 {symbol} 的名称")
    finally:
        quote_ctx.close()
