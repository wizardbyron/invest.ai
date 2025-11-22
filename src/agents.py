
import os

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from langchain_core.messages import HumanMessage, SystemMessage

from src.data import history_klines, get_stock_name
from src.indicators import pivot_points_table
from src.llm import create_chat
from src.util import remove_leading_spaces, get_timezone_by_type, in_trading_time, identify_stock_type, disclaimer_text


def trade_agent(symbol: str, end_date: str) -> str:
    if symbol is None:
        raise ValueError("symbol is required")

    llm_service = os.environ.get("LLM_SERVICE")
    model = os.environ.get("MODEL")
    days_off = 100

    name = get_stock_name(symbol)
    timezone = ZoneInfo(get_timezone_by_type(identify_stock_type(symbol)))
    now = datetime.now(timezone)
    start_date = (now - timedelta(days=days_off)).strftime('%Y-%m-%d')

    if end_date is None:
        end_date = now.strftime('%Y-%m-%d')

    df_daily = history_klines(
        symbol=symbol,
        period='daily',
        start_date=start_date,
        end_date=end_date)

    df_weekly = history_klines(
        symbol=symbol,
        period='weekly',
        start_date=start_date,
        end_date=end_date)

    df_monthly = history_klines(
        symbol=symbol,
        period='monthly',
        start_date=start_date,
        end_date=end_date)

    df_daily = df_daily.drop(['股票代码', '股票名称'], axis=1)
    df_weekly = df_weekly.drop(['股票代码', '股票名称'], axis=1)
    df_monthly = df_monthly.drop(['股票代码', '股票名称'], axis=1)

    # 获取上一个交易日的交易数据
    if df_daily.iloc[-1]['日期'] == end_date and in_trading_time():
        # df_last_day = df_daily[-2:-1]  # 交易时间内，获取上一个交易日的数据
        df_past = df_daily[-days_off:-1]  # 获取过去days_off天的数据
    else:
        # df_last_day = df_daily[-1:]
        df_past = df_daily[-days_off:]  # 获取过去days_off天的数据

    df_today = df_daily[-1:]

    # 获取上周的交易数据周线
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

    guide_prompt = f"""
    以下是某股票最近的交易数据:

    最近 {len(df_past)} 个交易日 K 线数据如下:

    {df_past.to_markdown(index=False)}

    均线数据计算如下：

    * 5 日均线: {df_daily["收盘"][-5:].mean():.2f}
    * 10 日均线: {df_daily["收盘"][-10:].mean():.2f}
    * 20 日均线: {df_daily["收盘"][-20:].mean():.2f}
    * 30 日均线: {df_daily["收盘"][-30:].mean():.2f}
    * 60 日均线: {df_daily["收盘"][-60:].mean():.2f}

    以下是该股票不同级别的枢轴点参考:

    根据上周K线生成的枢轴点 (参考周起始日：{df_last_week["日期"].iloc[-1]})：
    {pivot_points_table(df_last_week)['斐波那契'].to_markdown()}

    根据上月K线生成的枢轴点（参考月起始日：{df_last_month["日期"].iloc[-1]}）：
    {pivot_points_table(df_last_month)['斐波那契'].to_markdown()}

    结合以上历史交易的价格、成交量、均线和不同级别的枢轴点综合分析输出交易参考, 输出要求格式如下：

    ##### 价格参考

    - 买入价格范围:
    - 卖出价格范围:
    - 止盈价:
    - 止损价:

    ##### 交易策略

    - 短期策略:
    - 中期策略:
    - 长期策略:

    ##### 股票交易分析
    """

    guide_messages = [
        SystemMessage(
            content="你是一个资深量化交易员，可以根据市场交易数据给出专业的交易建议。"
        ),
        HumanMessage(
            content=remove_leading_spaces(guide_prompt)
        )
    ]

    chat = create_chat(llm_service, model)
    resp_guide = chat.invoke(guide_messages).content

    trade_prompt = f"""

    根据以下某股票交易参考:

    {resp_guide}

    以下是该股票最新的交易数据:

    {df_today.to_markdown()}

    请严格遵循交易参考，并根据最新的交易数据，给出最新的交易建议，输出要求格式如下：

    - 交易建议：买入/卖出/观望
    - 交易价格，如果交易建议为观望，则无需输出。
    - 原因说明

    """

    trade_messages = [
        SystemMessage(
            content="你是一个资深量化交易员，可以根据市场交易数据给出专业的交易建议。"
        ),
        HumanMessage(
            content=remove_leading_spaces(trade_prompt)
        )
    ]

    chat = create_chat(llm_service, model)
    resp_trade = chat.invoke(trade_messages).content

    result = f"""
    ### {name}({symbol}) 交易参考

    交易参考日: {df_daily["日期"].iloc[-1]}

    #### 交易建议

    {resp_trade}

    #### 交易参考

    {resp_guide}

    #### 声明

    {disclaimer_text}

    生成时间: {now.strftime("%Y-%m-%d %H:%M:%S")}
    分析模型: {model}
    """
    return remove_leading_spaces(result)
