from src.data import history_klines
from src.indicators import merge_points, pivot_points_table


def pivot_points_grid(symbol: str, period: str, series: str = "中间值") -> dict:
    """枢轴点网格交易策略

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
