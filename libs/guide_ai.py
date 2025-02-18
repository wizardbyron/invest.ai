from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from langchain_community.document_loaders import DataFrameLoader
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd

from libs.utils.data import history_klines
from libs.utils.indicators import pivot_points
from libs.utils.tools import remove_leading_spaces, DISCLIAMER
from libs.utils.chat_model import chat_models


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

        print(df_last_day)
        print(df_last_week)
        print(df_last_month)

        prompt = f"""以下是{name}({symbol})最近的交易数据

        近30 个交易日 K 线如下:

        {df_daily[-30:]}

        上个交易日 ({df_last_day["日期"].iloc[-1]}) 枢轴点：

        {pivot_points(df_last_day).to_markdown()}

        上周枢轴点 ({df_last_week["日期"].iloc[-1]})：

        {pivot_points(df_last_week).to_markdown()}

        上月枢轴点（{df_last_month["日期"].iloc[-1]}）：

        {pivot_points(df_last_month).to_markdown()}

        均线：如下

        * 5 日均线: {df_daily["收盘"][-5:].mean():.2f}
        * 10 日均线: {df_daily["收盘"][-10:].mean():.2f}
        * 20 日均线: {df_daily["收盘"][-20:].mean():.2f}
        * 30 日均线: {df_daily["收盘"][-30:].mean():.2f}

        请根据上述信息给出交易建议，规则如下：

        - 请用买入/卖出/观望给出交易建议和交易注意事项。如果是买入/卖出请给出价格。按照以下格式：

        ## 交易建议

        ## 注意事项

        如果需要额外的参考数据，请告诉我。
        """

        messages = [
            SystemMessage(
                content="你是一个量化交易员，可以根据数据给出专业的股票/ETF 交易建议。"
            ),
            HumanMessage(
                content=prompt
            )
        ]
        response = chat_models['deepseek'].invoke(messages)

        output_md = f""" # {symbol} - {name}

        {response.content}

        ## 提示词

        {remove_leading_spaces(prompt)}

        """

        output_md = remove_leading_spaces(output_md)

        file_path = f"docs/guide/{market}/{symbol}.md"

        with open(file_path, "w") as f:
            f.write(output_md)
