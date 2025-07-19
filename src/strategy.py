from pandas import DataFrame

from src.data import history_klines
from src.indicators import merge_points, pivot_points_table
from src.util import in_trading_time, is_weekday


def pivot_points_grid(symbol: str, period: str, series: str = "中间值") -> tuple[str, DataFrame]:
    """枢轴点网格交易法

    Args:
        symbol (str): 股票代码
        period (str, optional): 级别. 'weekly'/'daily'.
        series (str, optional): 枢轴点系列. Defaults to "中间值".

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

    tzone, klines = history_klines(symbol, period)

    if period == "daily":
        if in_trading_time(tzone):
            data = klines[-2:-1]  # 交易日时段取前一天数据
        else:
            data = klines[-1:]  # 非交易时段取最后一条数据
    elif period == "weekly":
        if is_weekday():
            data = klines[-2:-1]  # 工作日取上一周数据
        else:
            data = klines[-1:]  # 周末取最后一条数据
    else:
        raise ValueError(f"错误的参数: {period}")

    points_table = pivot_points_table(data)
    merged_points = merge_points(klines.iloc[-1], points_table, series)
    cur_price = merged_points.loc["*当前>", series]
    buy_price = merged_points.loc[f"支撑位{buy_point[period]:.1f}", series]
    sell_price = merged_points.loc[f"阻力位{sell_point[period]:.1f}", series]
    if cur_price > sell_price:
        msg = f"当前价格{cur_price}高于{period}阻力价格{sell_price}，建议卖出"
    elif cur_price < buy_price:
        msg = f"当前价格{cur_price}低于{period}支撑价格{buy_price}，建议买入"
    else:
        msg = f"当前价格{cur_price}在{period}支撑价格{buy_price}和阻力价格{sell_price}之间，建议观望"

    return msg, merged_points
