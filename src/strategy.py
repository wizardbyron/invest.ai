
import os

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from langchain_core.messages import HumanMessage, SystemMessage


from src.data import history_klines, get_stock_name
from src.llm import create_chat
from src.indicators import merge_points, pivot_points_table
from src.util import remove_leading_spaces, get_timezone_by_type


def pivot_points_grid(symbol: str, period: str, series: str = "参考价") -> dict:
    """基准价网格交易策略

    Args:
        symbol (str): 股票代码
        period (str, optional): 级别. 'weekly'/'daily'.
        series (str, optional): 基准价系列. Defaults to "参考价".

    Returns:
        tuple[str, float]: 返回交易建议
    """
    sell_point = {
        "weekly": 2.0,
        "daily": 1.5
    }

    buy_point = {
        "weekly": 2.0,
        "daily": 1.5
    }

    klines = history_klines(symbol, period)
    data = klines[-2:-1]
    points_table = pivot_points_table(data)
    merged_points = merge_points(klines.iloc[-1], points_table, series)
    cur_price = merged_points.loc["*当前>", series]
    buy_price = merged_points.loc[f"支撑位{buy_point[period]:.1f}", series]
    sell_price = merged_points.loc[f"阻力位{sell_point[period]:.1f}", series]
    if cur_price > sell_price:
        order = "卖出"
        msg = f"当前价格{cur_price}高于{period}阻力价格{sell_price}，建议卖出"
    elif cur_price < buy_price:
        order = "买入"
        msg = f"当前价格{cur_price}低于{period}支撑价格{buy_price}，建议买入"
    else:
        order = "观望"
        msg = f"当前价格{cur_price}在{period}支撑价格{buy_price}和阻力价格{sell_price}之间，建议观望"

    return {
        "points_table": points_table,
        "merged_table": merged_points,
        "order": order,
        "price": cur_price,
        "message": msg
    }


def ai_guide(symbol: str, end_date_str: str, days_off: int = 30) -> str:
    if symbol is None:
        raise ValueError("symbol is required")
    if days_off < 30:
        raise ValueError("days_off must be greater than or equal to 30")

    llm_service = os.environ.get("LLM_SERVICE")
    model = os.environ.get("MODEL")

    name = get_stock_name(symbol)
    timezone = ZoneInfo(get_timezone_by_type(get_timezone_by_type(symbol)))
    now = datetime.now(timezone)

    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    start_date = end_date - timedelta(days=days_off)
    start_date_str = start_date.strftime("%Y%m%d")

    df_daily = history_klines(
        symbol=symbol,
        period='daily',
        start_date=start_date_str,
        end_date=end_date_str)

    df_weekly = history_klines(
        symbol=symbol,
        period='weekly',
        start_date=start_date_str,
        end_date=end_date_str)

    df_monthly = history_klines(
        symbol=symbol,
        period='monthly',
        start_date=start_date_str,
        end_date=end_date_str)

    # 获取上一个交易日的交易数据
    if df_daily.iloc[-1]['日期'] == end_date.strftime('%Y-%m-%d') and now.hour < 16:
        df_last_day = df_daily[-2:-1]
    else:
        df_last_day = df_daily[-1:]

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

    points_md = f"""
    今日交易枢轴点 (参考最后一个交易日：{df_last_day["日期"].iloc[-1]})：
    {pivot_points_table(df_last_day).to_markdown()}

    本周交易枢轴点 (参考最后一个交易日：{df_last_week["日期"].iloc[-1]})：
    {pivot_points_table(df_last_week).to_markdown()}

    本月交易枢轴点（参考最后一个交易日：{df_last_month["日期"].iloc[-1]}）：
    {pivot_points_table(df_last_month).to_markdown()}
    """

    trade_md = f"""
    最近 {days_off} 个交易日 K 线数据如下:
    {df_daily[-days_off:].to_markdown(index=False)}

    均线数据计算如下：
    * 5 日均线: {df_daily["收盘"][-5:].mean():.2f}
    * 10 日均线: {df_daily["收盘"][-10:].mean():.2f}
    * 20 日均线: {df_daily["收盘"][-20:].mean():.2f}
    * 30 日均线: {df_daily["收盘"][-30:].mean():.2f}
    """

    prompt = f"""
    以下是{name}({symbol})最近的交易数据:

    {trade_md}

    以下是{name}({symbol})不同级别的交易基准价参考:

    {points_md}

    请结合价格、成交量、均线和不同级别的交易基准价综合分析输出交易建议, 输出要求如下：
    - 输出建议的买入和卖出价格，并输出分析过程。
    - 给出交易先后策略。
    - 给出期权交易策略。
    """

    format_prompt = """按照以下格式输出：
    ## 股票交易建议
    股票交易建议（包含股票交易价格）

    ## 期权交易建议
    期权交易建议（包含期权交易价格）

    ## 股票交易分析

    ## 期权交易分析
    """

    prompt = remove_leading_spaces(prompt+format_prompt)

    messages = [
        SystemMessage(
            content="你是一个日内交易的量化交易员，可以根据数据给出专业的交易建议。"
        ),
        HumanMessage(
            content=prompt
        )
    ]

    chat = create_chat(llm_service, model)
    return chat.invoke(messages).content
