import akshare as ak

# 预读取股票代码
us_symbol_dict = ak.stock_us_spot_em()


def history_klines(type: str,
                   symbol: str,
                   period: str = 'daily',
                   start_date: str = '',
                   end_date: str = '',
                   adjust_flag: str = 'qfq'):
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
        _type_: 返回 df
    """
    if type == 'A股':
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id21
        klines = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)

    elif type == 'A股ETF':
        # 参考: https://akshare.akfamily.xyz/data/fund/fund_public.html#id10
        klines = ak.fund_etf_hist_em(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)

    elif type == '港股':
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id66
        klines = ak.stock_hk_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)

    elif type == '美股':
        stock = us_symbol_dict[us_symbol_dict["代码"].str.endswith(f'.{symbol}')]
        code = stock['代码'].values[0]
        # 参考: https://akshare.akfamily.xyz/data/stock/stock.html#id56
        klines = ak.stock_us_hist(
            symbol=code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust=adjust_flag)

    else:
        klines = None

    klines['日期'] = klines['日期'].astype(str)
    if len(klines) == 0:
        raise ValueError(f"结果为空, 请检查参数")

    return klines
