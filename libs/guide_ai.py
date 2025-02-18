from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time

from langchain_community.document_loaders import DataFrameLoader
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd

from libs.utils.data import history_klines
from libs.utils.indicators import pivot_points
from libs.utils.tools import remove_leading_spaces, DISCLIAMER
from libs.utils.chat_model import get_chat_model

timezone = ZoneInfo('Asia/Shanghai')


def ai_guide():
    now = datetime.now(timezone)
    now_str = now.strftime("%Y-%m-%d  %H:%M:%S")
    today = datetime.today()
    today_str = today.strftime("%Y%m%d")
    start_date = today - timedelta(days=100)
    start_date_str = start_date.strftime("%Y%m%d")

    df_input = pd.read_csv("input/portfolio.csv", dtype={"代码": str})
    for index, row in df_input.iterrows():
        print(row)

        type = row["类型"]
        symbol = row["代码"]
        name = row["名称"]

        market, df_monthly = history_klines(
            type=type,
            symbol=symbol,
            period='monthly',
            start_date=start_date_str,
            end_date=today_str)

        market, df_weekly = history_klines(
            type=type,
            symbol=symbol,
            period='weekly',
            start_date=start_date_str,
            end_date=today_str)

        market, df_daily = history_klines(
            type=type,
            symbol=symbol,
            period='daily',
            start_date=start_date_str,
            end_date=today_str)

        # 获取上周的交易数据
        if df_daily.iloc[-1]['日期'] == now_str[:10] and now.hour < 15:  # 今天收盘
            df_last_day = df_daily[-2:-1]
        else:  # 非交易日
            df_last_day = df_daily[-1:]

        # 获取上周的交易数据
        if df_weekly.iloc[-1]['日期'] == now_str[:10]:  # 交易日
            df_last_week = df_weekly[-2:-1]
        else:  # 非交易日
            df_last_week = df_weekly[-1:]

        # 获取上月的交易数据
        if df_monthly.iloc[-1]['日期'] == now_str[:10]:  # 交易日
            df_last_month = df_monthly[-2:-1]
        else:  # 非交易日
            df_last_month = df_monthly[-1:]

        prompt = f"""以下是{name}({symbol})最近的交易数据

        最近 10 个交易日 K 线数据如下:

        {df_daily[-10:].to_markdown()}

        上周枢轴点 ({df_last_week["日期"].iloc[-1]})：

        {pivot_points(df_last_week).to_markdown()}

        上月枢轴点（{df_last_month["日期"].iloc[-1]}）：

        {pivot_points(df_last_month).to_markdown()}

        均线数据：

        * 5 日均线: {df_daily["收盘"][-5:].mean():.2f}
        * 10 日均线: {df_daily["收盘"][-10:].mean():.2f}
        * 20 日均线: {df_daily["收盘"][-20:].mean():.2f}
        * 30 日均线: {df_daily["收盘"][-30:].mean():.2f}

        请根据上述信息给出交易建议，规则如下：

        - 请用买入、卖出、观望三个交易建议之一。
        - 如果交易建议是买入或者卖出，在给交易建议的时候还需要输出相应的买入价格或者卖出价格。
        - 输出交易建议的分析过程，为什么选择这个买入价格或者卖出价格。
        - 根据股票或者ETF的特点给出交易中的注意事项以及需要参考的其它数据。
        
        按照以下格式输出：

        ## 交易建议

        买入或者卖出（价格：）

        ## 交易分析

        ## 注意事项

        ## 其它参考数据

        """

        prompt = remove_leading_spaces(prompt)

        print(prompt)

        messages = [
            SystemMessage(
                content="你是一个量化交易员，可以根据数据给出专业的交易建议。并且会在信息不足的时候，提出问题以获得更多的参考信息。"
            ),
            HumanMessage(
                content=prompt
            )
        ]
        chat = get_chat_model("zhipuai", "glm-4-flash")

        response = chat.invoke(messages)

        print(response.content)

        output_md = f""" # {symbol} - {name}

        更新时间: {now_str}

        模型: {chat.model_name}

        {response.content}

        ## 提示词

        {prompt}

        """

        output_md = remove_leading_spaces(output_md)

        file_path = f"docs/guide/{market}/{symbol}.md"

        with open(file_path, "w") as f:
            f.write(output_md)
