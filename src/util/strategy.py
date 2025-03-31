from pandas import DataFrame


def intraday(points: DataFrame):
    cur_price = points.loc["*当前>", "中间值"]
    if points.loc["*开盘", "中间值"] > points.loc["*昨收", "中间值"]:  # 高开
        buy_point = "支撑位0.5"
        sell_point = "阻力位1.5"
    else:  # 低开
        buy_point = "支撑位1.5"
        sell_point = "阻力位0.5"
    buy_price = points.loc[buy_point, "中间值"]
    sell_price = points.loc[sell_point, "中间值"]
    if cur_price > sell_price:
        print(f"当前价格{cur_price}高于{sell_price}，建议卖出")
    elif cur_price < buy_price:
        print(f"当前价格{cur_price}低于{buy_price}，建议买入")
    else:
        print(f"当前价格{cur_price}在{buy_price}和{sell_price}之间，观望")
    print("="*40)


def weekly(points: DataFrame):
    cur_price = points.loc["*当前>", "中间值"]
    buy_price = points.loc["支撑位2.0", "中间值"]
    sell_price = points.loc["阻力位2.0", "中间值"]
    if cur_price > sell_price:
        print(f"当前价格{cur_price}高于{sell_price}，建议卖出")
    elif cur_price < buy_price:
        print(f"当前价格{cur_price}低于{buy_price}，建议买入")
    else:
        print(f"当前价格{cur_price}在{buy_price}和{sell_price}之间，观望")
    print("="*40)
