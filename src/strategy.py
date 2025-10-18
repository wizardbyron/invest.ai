
import os

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from langchain_core.messages import HumanMessage, SystemMessage


from src.data import history_klines, get_stock_name
from src.llm import create_chat
from src.indicators import merge_points, pivot_points_table
from src.util import remove_leading_spaces, get_timezone_by_type, in_trading_time, disclaimer_text


def pivot_points_grid(symbol: str,
                      period: str,
                      start_date: str,
                      end_date: str,
                      point_type: str) -> dict:
    """基准价网格交易策略

    Args:
        symbol (str): 股票代码
        period (str, optional): 级别. 'weekly'/'daily'.
        series (str, optional): 基准价系列. Defaults to "中值".

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

    klines = history_klines(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date)
    data = klines[-2:-1]
    points_table = pivot_points_table(data)
    merged_points = merge_points(klines.iloc[-1], points_table, point_type)
    cur_price = merged_points.loc["*当前>", point_type]
    buy_price = merged_points.loc[f"支撑位{buy_point[period]:.1f}", point_type]
    sell_price = merged_points.loc[f"阻力位{sell_point[period]:.1f}", point_type]
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


def ai_guide(symbol: str,
             end_date: str,
             days_off: int = 100) -> str:
    if symbol is None:
        raise ValueError("symbol is required")
    if days_off < 100:
        raise ValueError("days_off must be greater than or equal to 100")

    name = get_stock_name(symbol)
    timezone = ZoneInfo(get_timezone_by_type(get_timezone_by_type(symbol)))
    now = datetime.now(timezone)
    start_date = (now - timedelta(days=days_off)).strftime('%Y-%m-%d')

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

    # 获取上一个交易日的交易数据
    if df_daily.iloc[-1]['日期'] == end_date and in_trading_time():
        df_last_day = df_daily[-2:-1]  # 交易时间内，获取上一个交易日的数据
        df_past = df_daily[-days_off:-1]  # 获取过去days_off天的数据
    else:
        df_last_day = df_daily[-1:]
        df_past = df_daily[-days_off:]  # 获取过去days_off天的数据

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

    prompt = f"""
    以下是某股票最近的交易数据:

    最近 {days_off} 个交易日 K 线数据如下:
    {df_past.to_markdown(index=False)}

    均线数据计算如下：
    * 5 日均线: {df_daily["收盘"][-5:].mean():.2f}
    * 10 日均线: {df_daily["收盘"][-10:].mean():.2f}
    * 20 日均线: {df_daily["收盘"][-20:].mean():.2f}
    * 30 日均线: {df_daily["收盘"][-30:].mean():.2f}

    以下是该股票不同级别的交易基准价参考:

    今日交易参考基准价 (参考最后一个交易日：{df_last_day["日期"].iloc[-1]})：
    {pivot_points_table(df_last_day).to_markdown()}

    本周交易参考基准价 (参考最后一个交易日：{df_last_week["日期"].iloc[-1]})：
    {pivot_points_table(df_last_week).to_markdown()}

    本月交易参考基准价（参考最后一个交易日：{df_last_month["日期"].iloc[-1]}）：
    {pivot_points_table(df_last_month).to_markdown()}

    最新交易情况如下:

    {df_last_day.to_markdown(index=False)}

    请结合最新交易数据以及历史交易的价格、成交量、均线和不同级别的交易基准价综合分析输出交易建议, 输出要求如下：
    - 输出买入和卖出价格，以及止盈点和止损点。
    - 输出出股票交易策略。
    - 输出分析过程。

    并按照以下格式输出：

    #### 交易参考

    - 买入价格范围:
    - 卖出价格范围:
    - 止盈点:
    - 止损点:

    **交易策略**:

    - 短期策略:
    - 中期策略:
    - 长期策略:

    #### 交易分析

    """

    messages = [
        SystemMessage(
            content="你是一个资深量化交易员，可以根据市场交易数据给出专业的交易建议。"
        ),
        HumanMessage(
            content=remove_leading_spaces(prompt)
        )
    ]

    llm_service = os.environ.get("LLM_SERVICE", "zai")
    model = os.environ.get("MODEL", "glm-4.5-flash")
    chat = create_chat(llm_service, model)
    resp = chat.invoke(messages).content

    result = f"""
    ### {name}({symbol})

    交易参考日: {now.strftime("%Y-%m-%d")}

    {resp}

    #### 声明

    {disclaimer_text}

    生成时间: {now.strftime("%Y-%m-%d %H:%M:%S")}
    """
    return remove_leading_spaces(result)
