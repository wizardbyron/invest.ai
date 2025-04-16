import time
import akshare as ak
import fire


def hs300(up=20.5, down=18.5):

    df_hs300_pe = ak.stock_index_pe_lg(symbol="沪深300")
    df_hs300_pe = df_hs300_pe[["日期", "静态市盈率中位数"]]

    last_day_pe = df_hs300_pe.iloc[-1]

    print(last_day_pe)
    if last_day_pe["静态市盈率中位数"] > up:
        print("沪深300估值偏高，注意减仓")
    elif last_day_pe["静态市盈率中位数"] < down:
        print("沪深300估值偏低，注意加仓")
    else:
        print("沪深300估值适当，持有观望")


def bonds():
    df_bond_zh_us_rate = ak.bond_zh_us_rate(start_date="19901219")
    df_bond_zh_us_rate[["日期", "中国国债收益率10年", "美国国债收益率10年"]]
    print(df_bond_zh_us_rate[-100:])


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire()
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
