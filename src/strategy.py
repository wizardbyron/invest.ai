from pandas import DataFrame

from src.data import history_klines
from src.indicators import pivot_points_table, merge_points
from src.util import in_trading_time, is_weekend

sell_point = {
    "weekly": 2.0,
    "daily": 1.5
}

buy_point = {
    "weekly": 2.0,
    "daily": 1.5
}


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
    if in_trading_time(tzone):
        data = klines[-2:-1]
    else:
        if is_weekend() or period == "daily":
            data = klines[-1:]
        else:
            data = klines[-2:-1]

    points = merge_points(klines.iloc[-1],
                          pivot_points_table(data),
                          series)
    print(f"\n{symbol}-{period}:\n{data}\n{points}")
    return points


def pivot_points_grid(symbol: str, period: str, series: str = "中间值") -> tuple[str, float]:
    """枢轴点网格策略

    Args:
        points (DataFrame): 合并后的枢轴点数据
        buy_point (float, optional): 买点，支撑位. Defaults to 2.
        sell_point (float, optional): 卖点，阻力位. Defaults to 2.

    Returns:
        _type_: _description_
    """
    points = get_points(symbol, period, series)
    cur_price = points.loc["*当前>", series]
    buy_price = points.loc[f"支撑位{buy_point[period]:.1f}", series]
    sell_price = points.loc[f"阻力位{sell_point[period]:.1f}", series]
    if cur_price > sell_price:
        print(f"{symbol}当前价格{cur_price}高于{period}阻力价格{sell_price}，建议卖出")
        return "卖出", cur_price
    elif cur_price < buy_price:
        print(f"{symbol}当前价格{cur_price}低于{period}支撑价格{buy_price}，建议买入")
        return "买入", cur_price
    else:
        print(f"{symbol}当前价格{cur_price}在{period}支撑价格{buy_price}和阻力价格{sell_price}之间，观望")
        return "持有", cur_price
