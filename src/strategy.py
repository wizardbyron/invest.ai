from pandas import DataFrame


def pivot_points_grid(points: DataFrame, buy_point: float, sell_point: float, series="中间值"):
    """枢轴点网格策略

    Args:
        points (DataFrame): 合并后的枢轴点数据
        buy_point (float, optional): 买点，支撑位. Defaults to 2.
        sell_point (float, optional): 卖点，阻力位. Defaults to 2.

    Returns:
        _type_: _description_
    """
    cur_price = points.loc["*当前>", series]
    buy_price = points.loc[f"支撑位{buy_point:.1f}", series]
    sell_price = points.loc[f"阻力位{sell_point:.1f}", series]
    if cur_price > sell_price:
        print(f"当前价格{cur_price}高于{sell_price}，建议卖出")
        return "卖出", cur_price
    elif cur_price < buy_price:
        print(f"当前价格{cur_price}低于{buy_price}，建议买入")
        return "买入", cur_price
    else:
        print(f"当前价格{cur_price}在{buy_price}和{sell_price}之间，观望")
        return "持有", cur_price
