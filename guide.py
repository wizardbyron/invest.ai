from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os


from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd

from src.util.data import history_klines
from src.util.llm import create_chat
from src.util.indicators import pivot_points
from src.util.tools import remove_leading_spaces, append_discliamer

timezone = ZoneInfo('Asia/Shanghai')
now = datetime.now(timezone)
now_str = now.strftime("%Y-%m-%d %H:%M:%S")
today = datetime.today()
today_str = today.strftime("%Y%m%d")
start_date = today - timedelta(days=100)
start_date_str = start_date.strftime("%Y%m%d")

llm_service = os.environ.get("LLM_SERVICE")
model = os.environ.get("MODEL")

df_input = pd.read_csv("input/selected.csv", dtype={"代码": str})
for index, row in df_input.iterrows():
    print(row)

    type = row["类型"]
    symbol = row["代码"]
    name = row["名称"]

    df_daily = history_klines(
        type=type,
        symbol=symbol,
        period='daily',
        start_date=start_date_str,
        end_date=today_str)

    df_weekly = history_klines(
        type=type,
        symbol=symbol,
        period='weekly',
        start_date=start_date_str,
        end_date=today_str)

    df_monthly = history_klines(
        type=type,
        symbol=symbol,
        period='monthly',
        start_date=start_date_str,
        end_date=today_str)

    # 获取上一个交易日的交易数据
    if df_daily.iloc[-1]['日期'] == today.strftime('%Y-%m-%d'):
        df_last_day = df_daily[-2:-1]
    else:
        df_last_day = df_daily[-1:]

    # 获取上周的交易数据周线
    if type == "美股":
        df_last_week = df_weekly[-2:-1]
    else:
        if now.weekday() < 5:  # 交易日
            df_last_week = df_weekly[-2:-1]
        else:  # 非交易日
            df_last_week = df_weekly[-1:]

    # 获取上月的交易数据
    last_month = df_monthly["日期"].iloc[-1]
    this_month = now.strftime("%Y-%m")
    if last_month.startswith(this_month):
        df_last_month = df_monthly[-2:-1]
    else:
        df_last_month = df_monthly[-1:]

    points_md = f"""上个交易日枢轴点 ({df_last_day["日期"].iloc[-1]})：

    {pivot_points(df_last_day).to_markdown()}

    上周枢轴点 ({df_last_week["日期"].iloc[-1]})：

    {pivot_points(df_last_week).to_markdown()}

    上月枢轴点（{df_last_month["日期"].iloc[-1]}）：

    {pivot_points(df_last_month).to_markdown()}
    """

    trade_md = f"""最近 10 个交易日 K 线数据如下:

    {df_daily[-10:].to_markdown(index=False)}

    均线数据：

    * 5 日均线: {df_daily["收盘"][-5:].mean():.2f}
    * 10 日均线: {df_daily["收盘"][-10:].mean():.2f}
    * 20 日均线: {df_daily["收盘"][-20:].mean():.2f}
    * 30 日均线: {df_daily["收盘"][-30:].mean():.2f}
    """

    prompt = f"""
    以下是{name}({symbol})最近的交易数据:

    {trade_md}

    以下是{name}({symbol})的枢轴点数据:

    {points_md}

    请结合价格、成交量、均线和枢轴点综合分析输出交易建议, 输出要求如下：

    - 输出建议的买入和卖出价格，并输出分析过程。
    - 给出交易先后策略。

    """

    format_prompt = """按照以下格式输出：

    # 交易建议

    交易建议（交易价格）

    # 交易分析

    """

    prompt = remove_leading_spaces(prompt+format_prompt)

    # print(prompt)

    messages = [
        SystemMessage(
            content="你是一个量化交易员，可以根据数据给出专业的交易建议。并且会在信息不足的时候，提出问题以获得更多的参考信息。"
        ),
        HumanMessage(
            content=prompt
        )
    ]

    # chat = create_chat(llm_service, model)

    # response = chat.invoke(messages)

    # print(response.content)

    output_md = f"""# {symbol} - {name}

    更新时间: {now_str}

    {points_md}

    """
    output_md = append_discliamer(output_md)
    output_md = remove_leading_spaces(output_md)

    file_path = f"docs/交易指南/{type}/{symbol}.md"

    with open(file_path, "w") as f:
        f.write(output_md)
