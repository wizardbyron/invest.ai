#!/usr/bin/env python

import time
import akshare as ak
import fire
import pandas as pd

from src.data import cn_bond, us_bond


class MacroEconomic:
    """宏观经济分析
    """

    @classmethod
    def hs300(cls, up=20.5, down=18.5):
        """沪深300指数市盈率中位数判断

        Args:
            up (float, optional): _description_. Defaults to 20.5.
            down (float, optional): _description_. Defaults to 18.5.
        """
        df_hs300_pe = ak.stock_index_pe_lg(symbol="沪深300")
        df_hs300_pe = df_hs300_pe[["日期", "静态市盈率中位数"]]

        print(df_hs300_pe[-20:])
        last_day_pe = df_hs300_pe.iloc[-1]
        if last_day_pe["静态市盈率中位数"] > up:
            print("沪深300估值偏高，注意减仓")
        elif last_day_pe["静态市盈率中位数"] < down:
            print("沪深300估值偏低，注意加仓")
        else:
            print("沪深300估值适当，持有观望")

    @classmethod
    def intrest_rate(cls, period=10):
        """美国/中国/日本/欧洲 央行利率

        Args:
            period (int, optional): _description_. Defaults to 10.
        """
        df_usa = ak.macro_bank_usa_interest_rate()[-period:]
        df_usa = df_usa[df_usa["今值"].notna()]
        df_china = ak.macro_bank_china_interest_rate()[-period:]
        df_china = df_china[df_china["今值"].notna()]
        df_japan = ak.macro_bank_japan_interest_rate()[-period:]
        df_japan = df_japan[df_japan["今值"].notna()]
        df_euro = ak.macro_bank_euro_interest_rate()[-period:]
        df_euro = df_euro[df_euro["今值"].notna()]
        print(f"{df_usa}\n{df_china}\n{df_japan}\n{df_euro}\n")

    @classmethod
    def bonds(cls, country: str = "cn", days: int = 30):
        """十年国债收益率

        Args:
            country (str, optional): 国家，中国(cn)/美国(us). Defaults to "cn".
            days (int, optional): 交易日. Defaults to 30.
        """
        if country == "cn":
            df = cn_bond()[-days:]
            yield_min = df['收益率(%)'].min()
            yield_max = df['收益率(%)'].max()
        if country == "us":
            df = us_bond()[:days].sort_values(by='Date')
            yield_min = df['10 Yr'].min()
            yield_max = df['10 Yr'].max()
        print(df)
        print(f'{days}日最大收益率:{yield_max}')
        print(f'{days}日最小收益率:{yield_min}')

    @classmethod
    def zh_pmi(cls):
        '''穿越周期指数：

        数据来源: https://data.stats.gov.cn/easyquery.htm?cn=A01&zb=A0B01
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

    @classmethod
    def zh_gold(cls):
        '''黄金储备

        数据来源: http://www.pbc.gov.cn/diaochatongjisi/resource/cms/2025/07/2025070716001083396.htm
        '''
        url = "http://www.pbc.gov.cn/diaochatongjisi/resource/cms/2025/07/2025070716001083396.htm"
        df_raw = pd.read_html(url)[0]
        df = df_raw.loc[[2, 8]].dropna(axis=1).iloc[:, 1::2]
        data = {
            "月份": df.values[0].tolist(),
            "黄金储备(亿美元)": df.values[1].tolist()
        }
        new_df = pd.DataFrame(data)

        print(new_df)

    @classmethod
    def zh_cpi_ppi(cls, months=24):
        """CPI和PPI剪刀差

        Args:
            months (int, optional): _description_. Defaults to 24.
        """
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

    @classmethod
    def exchange_rate(cls, days=30):
        """离岸人民币和在岸人民币汇率差
        """
        df_usd_cnh = ak.forex_hist_em(symbol="USDCNH")[-days:]
        df_usd_cnh = df_usd_cnh.set_index("日期")
        df_usd_cnyc = ak.forex_hist_em(symbol="USDCNYC")[-days:]
        df_usd_cnyc = df_usd_cnyc.set_index("日期")
        df = pd.concat([df_usd_cnh, df_usd_cnyc], axis=1, join="outer")
        df["汇差"] = df_usd_cnh['最新价']-df_usd_cnyc['最新价']
        print(df)

    @classmethod
    def china(cls):
        """中国宏观经济分析
        """
        df_money = ak.macro_china_money_supply()[:12]  # 货币供应量
        print(df_money)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(MacroEconomic)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
