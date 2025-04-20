import time
import akshare as ak
import fire
import pandas as pd


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


def bonds(days=30):
    df_bond_zh_us_rate = ak.bond_zh_us_rate(start_date="19901219")
    df_bond_zh_us_rate = df_bond_zh_us_rate[["日期", "中国国债收益率10年", "美国国债收益率10年"]]
    print(df_bond_zh_us_rate[-days:])
    ak.macro_china_pmi_yearly


def intrest_rate(period=10):
    df_usa = ak.macro_bank_usa_interest_rate()[-period:]
    df_usa = df_usa[df_usa["今值"].notna()]
    df_china = ak.macro_bank_china_interest_rate()[-period:]
    df_china = df_china[df_china["今值"].notna()]
    df_japan = ak.macro_bank_japan_interest_rate()[-period:]
    df_japan = df_japan[df_japan["今值"].notna()]
    df_euro = ak.macro_bank_euro_interest_rate()[-period:]
    df_euro = df_euro[df_euro["今值"].notna()]


def pmi():
    '''穿越周期指数：
    PMI两期新订单差值-两期产成品库存差值

    预期需求 - 真实需求
    > 0(补库存周期)
    < 0(去库存周期)
    '''

    df = pd.read_excel("input/pmi_china.xls", header=None)[2:15]
    df = df.T
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    df.reset_index(drop=True)
    df["经济势能"] = df["新订单指数(%)"]-df["产成品库存指数(%)"]

    for idx, row in df.iterrows():
        if idx == len(df):
            break
        df.loc[idx, "穿越周期指数"] = df.loc[idx, "经济势能"]-df.loc[idx+1, "经济势能"]

    print(df[["指标", "新订单指数(%)", "产成品库存指数(%)", "经济势能", "穿越周期指数"]])


def zh_cpi_ppi(months=24):
    zh_cpi_cols = ["月份", "全国-当月", "全国-同比增长", "全国-环比增长", "全国-累计"]
    df_zh_cpi = ak.macro_china_cpi()[zh_cpi_cols]
    df_zh_ppi = ak.macro_china_ppi()
    df = pd.DataFrame({
        "月份": df_zh_cpi["月份"],
        "CPI-当月": df_zh_cpi["全国-当月"],
        "CPI-同比增长": df_zh_cpi["全国-同比增长"],
        "CPI-环比增长": df_zh_cpi["全国-环比增长"],
        "CPI-累计": df_zh_cpi["全国-累计"],
        "PPI-当月": df_zh_ppi["当月"],
        "PPI-当月同比增长": df_zh_ppi["当月同比增长"],
        "PPI-累计": df_zh_ppi["累计"],
        "CPI-PPI差值": df_zh_cpi["全国-当月"]-df_zh_ppi["当月"],
    })
    df = df[:months]
    print(df)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire()
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
