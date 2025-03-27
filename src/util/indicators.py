from pandas import DataFrame
import pandas as pd


def classic(high: float, low: float, close: float) -> dict[str, float]:
    """
    计算经典支撑位和阻力位
    :param high: 最高价
    :param low: 最低价
    :param close: 收盘价
    :return: 经典支撑位和阻力位
    """
    p = (high + low + close)/3

    s1 = 2 * p - high
    s2 = p - (high - low)
    s3 = low - 2 * (high - p)

    r1 = 2 * p - low
    r2 = p + (high - low)
    r3 = high + 2 * (p - low)

    return {
        "阻力位3": r3,
        "阻力位2.5": (r2+r3)/2,
        "阻力位2": r2,
        "阻力位1.5": (r1+r2)/2,
        "阻力位1": r1,
        "阻力位0.5": (p+r1)/2,
        "枢轴点": p,
        "支撑位0.5": (p+s1)/2,
        "支撑位1": s1,
        "支撑位1.5": (s1+s2)/2,
        "支撑位2": s2,
        "支撑位2.5": (s2+s3)/2,
        "支撑位3": s3
    }


def fibonacci(high: float, low: float, close: float) -> dict[str, float]:
    """
    计算斐波那契支撑位和阻力位
    :param high: 最高价
    :param low: 最低价
    :param close: 收盘价
    :return: 斐波那契支撑位和阻力位
    """
    p = (high + low + close)/3
    s1 = p - (high - low) * 0.382
    s2 = p - (high - low) * 0.618
    s3 = p - (high - low)
    r1 = p + (high - low) * 0.382
    r2 = p + (high - low) * 0.618
    r3 = p + (high - low)

    return {
        "阻力位3": r3,
        "阻力位2.5": (r2+r3)/2,
        "阻力位2": r2,
        "阻力位1.5": (r1+r2)/2,
        "阻力位1": r1,
        "阻力位0.5": (p+r1)/2,
        "枢轴点": p,
        "支撑位0.5": (p+s1)/2,
        "支撑位1": s1,
        "支撑位1.5": (s1+s2)/2,
        "支撑位2": s2,
        "支撑位2.5": (s2+s3)/2,
        "支撑位3": s3
    }


def pivot_points(df_input: DataFrame) -> DataFrame:
    high = df_input["最高"].max()
    low = df_input["最低"].min()
    close = df_input["收盘"].iloc[-1]

    c_points = classic(high, low, close)
    f_points = fibonacci(high, low, close)

    item = {"经典": c_points, "斐波那契": f_points}
    row_index = c_points.keys()
    df_output = pd.DataFrame(item, index=row_index)
    df_output["中间值"] = (df_output["经典"] + df_output["斐波那契"])/2

    p = c_points["枢轴点"]
    df_output["中间值波动率"] = (df_output["中间值"] - p)/p
    df_output["中间值波动率"] = df_output["中间值波动率"].map(lambda x: '{:.2%}'.format(x))

    df_output = df_output.round(3)
    return df_output


def merge_points(klines: DataFrame) -> DataFrame:
    points = pivot_points(klines[-2:-1])
    points.loc["*昨收"] = klines.iloc[-2]["收盘"]
    today = klines.iloc[-1]
    points.loc["*最高"] = today["最高"]
    points.loc["*开盘"] = today["开盘"]
    points.loc["*最低"] = today["最低"]
    points.loc["*当前>"] = today["收盘"]
    latest = today["收盘"]
    points["波动率"] = (points["中间值"] - latest)/latest
    points["波动率"] = points["波动率"].map(lambda x: '{:.2%}'.format(x))
    points = points.sort_values(by="中间值", ascending=False)
    points = points[["中间值", "波动率"]]
    points = points.round(3)
    return points
