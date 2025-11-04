#!/usr/bin/env python

import datetime
import os
import time

import akshare as ak
import fire
import pandas as pd
import requests

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_core.messages import HumanMessage, SystemMessage

from src.data import cn_bond, us_bond
from src.llm import create_chat
from src.util import remove_leading_spaces

load_dotenv()


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
        '''中国人民银行黄金储备

        数据来源: http://www.pbc.gov.cn/diaochatongjisi/116219/116319/5570903/5570886/index.html
        '''

        base_url = "http://www.pbc.gov.cn/diaochatongjisi/116219/116319/5570903/5570886/index.html"

        # 发送HTTP请求获取页面内容
        response = requests.get(base_url)
        html_content = response.text

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'lxml')  # 你也可以使用'html.parser'

        # 查找所有的<a>标签
        a_tags = soup.find_all('a')

        # 列表用于存储文本为"htm"的链接地址
        links_with_htm_text = []

        # 遍历所有<a>标签
        for a in a_tags:
            # 获取<a>标签的文本内容
            text = a.get_text()
            # 检查文本内容是否为"htm"
            if text == "htm":
                # 获取<a>标签的href属性值
                href = a.get('href')
                # 添加到列表中
                links_with_htm_text.append(href)

        # 提取链接
        target_url = f'http://www.pbc.gov.cn/{links_with_htm_text[0]}'
        df_raw = pd.read_html(target_url)[0]
        df = df_raw.loc[[2, 8]].dropna(axis=1).iloc[:, 1::2]
        data = {
            "月份": df.values[0].tolist(),
            "黄金储备(亿美元)": df.values[1].tolist()
        }
        new_df = pd.DataFrame(data)

        print(new_df)

    @classmethod
    def zh_cpi_ppi(cls, months=12):
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
    def china(cls, months=12):
        """中国宏观经济分析
        """
        prompt = f"""
        今天是 {datetime.datetime.now().strftime("%Y-%m-%d")}

        请分析以下中国宏观经济数据，并给出分析结果：

        1. 离岸人民币汇率

        {ak.forex_hist_em(symbol="USDCNH")[-30:].to_markdown()}

        2. 在岸人民币汇率

        {ak.forex_hist_em(symbol="USDCNYC")[-30:].to_markdown()}

        3. 中国居民消费物价指数（CPI）

        {ak.macro_china_cpi()[:months].to_markdown()}

        4. 中国工业品出厂价格指数（PPI）

        {ak.macro_china_ppi()[:months].to_markdown()}

        5. 中国制造业采购经理指数（PMI）

        {pd.read_excel("input/pmi_china.xls").to_markdown()}

        6. 十年期国债收益率

        {cn_bond()[-30:].to_markdown()}

        7. 中国人民银行利率

        {ak.macro_bank_china_interest_rate()[-5:].to_markdown()}

        8. 存款准备金率

        {ak.macro_china_reserve_requirement_ratio()[:5].to_markdown()}

        9. 新增信贷数据

        {ak.macro_china_new_financial_credit()[:12].to_markdown()}

        请根据以上数据对当前的经济形势进行判断, 对未来三个月的经济走势和政策方向进行预测。

        并根据流动性定价的观点，判断对当前股市的影响。

        如果有其他需要的数据，请告诉我，我会提供。

        """

        prompt = remove_leading_spaces(prompt)

        messages = [
            SystemMessage(
                content="你是一个宏观经济分析专家，可以根据宏观经济数据对当前的经济形势和未来的经济走势进行分析。"
            ),
            HumanMessage(
                content=(prompt)
            )
        ]

        llm_service = os.environ.get("LLM_SERVICE")
        model = os.environ.get("MODEL")
        chat = create_chat(llm_service, model)
        resp = chat.invoke(messages).content
        print(resp)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(MacroEconomic)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
