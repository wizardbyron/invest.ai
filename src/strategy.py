from pandas import DataFrame

from src.data import history_klines
from src.indicators import merge_points, pivot_points_table
from src.util import in_trading_time, is_weekday


def get_points(symbol: str, period: str, series: str = "中间值") -> DataFrame:
    """将枢轴点和当前的价格进行合并

    Args:
        symbol (str): 股票代码
        series (str): "经典"/"斐波那契"/"中间值", defaults to "中间值"
        period (str): 周期，weekly or daily

    Returns:
        DataFrame: _description_
    """
    tzone, klines = history_klines(str(symbol), period)

    if period == "daily":
        if in_trading_time(tzone):
            data = klines[-2:-1]
        else:
            data = klines[-1:]
    elif period == "weekly":
        if is_weekday():
            data = klines[-2:-1]
        else:
            data = klines[-1:]
    else:
        raise ValueError(f"错误的参数: {period}")

    points_table = pivot_points_table(data)
    merged_points = merge_points(klines.iloc[-1], points_table, series)
    print(f"\n{symbol}-{period}:\n{data}\n{merged_points}")
    return merged_points


def pivot_points_grid(symbol: str, period: str, series: str = "中间值") -> tuple[str, float]:
    """_summary_

    Args:
        symbol (str): 股票代码
        period (str): 级别
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

    points = get_points(symbol, period, series)
    cur_price = points.loc["*当前>", series]
    buy_price = points.loc[f"支撑位{buy_point[period]:.1f}", series]
    sell_price = points.loc[f"阻力位{sell_point[period]:.1f}", series]
    if cur_price > sell_price:
        msg = f"{symbol}当前价格{cur_price}高于{period}阻力价格{sell_price}，建议卖出"
    elif cur_price < buy_price:
        msg = f"{symbol}当前价格{cur_price}低于{period}支撑价格{buy_price}，建议买入"
    else:
        msg = f"{symbol}当前价格{cur_price}在{period}支撑价格{buy_price}和阻力价格{sell_price}之间，观望"

    return msg, cur_price
