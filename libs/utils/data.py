import akshare as ak


def fetch_klines(type: str, symbol: str, start_date: str = '', end_date: str = '',  adjust_flag: str = ''):
    us_symbol_dict = ak.stock_us_spot_em()
    if type == 'A股':
        # https://akshare.akfamily.xyz/data/stock/stock.html#id21
        history_klines = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period='daily',
            adjust=adjust_flag)
        market = 'cn'
    elif type == 'A股ETF':
        # https://akshare.akfamily.xyz/data/fund/fund_public.html#id10
        history_klines = ak.fund_etf_hist_em(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period='daily',
            adjust=adjust_flag)
        market = 'cn'
    elif type == '港股':
        # https://akshare.akfamily.xyz/data/stock/stock.html#id66
        history_klines = ak.stock_hk_hist(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period='daily',
            adjust=adjust_flag)
        market = 'hk'
    elif type == '美股':
        stock = us_symbol_dict[us_symbol_dict["代码"].str.endswith(f'.{symbol}')]
        code = stock['代码'].values[0]
        # https://akshare.akfamily.xyz/data/stock/stock.html#id56
        history_klines = ak.stock_us_hist(
            symbol=code,
            start_date=start_date,
            end_date=end_date,
            period='daily',
            adjust=adjust_flag)
        market = 'us'
    else:
        market = None
        history_klines = None

    return market, history_klines
