from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from libs.utils.data import history_klines
from libs.utils.indicators import fibonacci, classic
from libs.utils.tools import remove_leading_spaces, DISCLIAMER

timezone = ZoneInfo('Asia/Shanghai')


def create_guide(level: int):
    now = datetime.now(timezone).replace(microsecond=0).replace(tzinfo=None)
    today = datetime.today()
    today_str = today.strftime("%Y%m%d")
    start_date = today - timedelta(days=100)
    start_date_str = start_date.strftime("%Y%m%d")

    df_input = pd.read_csv("input/selected.csv", dtype={"代码": str})
    df_output = df_input.copy()
    for index, row in df_input.iterrows():
        print(row)

        type = row["类型"]
        symbol = row["代码"]
        name = row["名称"]
        market, df_weekly = history_klines(
            type=type,
            symbol=symbol,
            period='weekly',
            start_date=start_date_str,
            end_date=today_str)

        market, df_daily = history_klines(
            type=type,
            symbol=symbol,
            period='daily',
            start_date=start_date_str,
            end_date=today_str)
        # 获取上周的交易数据
        df = df_weekly[-2:-1]

        print(df)

        start_date = df["日期"].iloc[0]
        end_date = df["日期"].iloc[-1]
        high = df["最高"].max()
        low = df["最低"].min()
        close = df["收盘"].iloc[-1]

        c_points = classic(high, low, close)
        f_points = fibonacci(high, low, close)

        item = {"经典": c_points, "斐波那契": f_points}
        row_index = c_points.keys()
        df_single = pd.DataFrame(item, index=row_index)
        df_single["中间值"] = (df_single["经典"] + df_single["斐波那契"])/2

        output_md = f"""# {symbol} - {name}

        更新时间: {now}

        ## 交易参考

        ### 周线枢轴点 ({end_date})

        {df_single.round(2).to_markdown()}

        ### 均线

        * 5 日均线: {df_daily["收盘"][-5:].mean():.2f}
        * 10 日均线: {df_daily["收盘"][-10:].mean():.2f}
        * 20 日均线: {df_daily["收盘"][-20:].mean():.2f}
        * 30 日均线: {df_daily["收盘"][-30:].mean():.2f}

        ## 免责声明

        {DISCLIAMER}

        """
        output_md = remove_leading_spaces(output_md)

        file_path = f"docs/guide/{market}/{symbol}.md"

        with open(file_path, "w") as f:
            f.write(output_md)

        df_output.loc[index, f"{level}日经典阻力位3"] = c_points["阻力位3"]
        df_output.loc[index, f"{level}日斐波那契阻力位3"] = f_points["阻力位3"]
        df_output.loc[index, f"{level}日经典阻力位2"] = c_points["阻力位2"]
        df_output.loc[index, f"{level}日斐波那契阻力位2"] = f_points["阻力位2"]
        df_output.loc[index, f"{level}日经典阻力位1"] = c_points["阻力位1"]
        df_output.loc[index, f"{level}日斐波那契阻力位1"] = f_points["阻力位1"]
        df_output.loc[index, f"{level}日枢轴点"] = c_points["枢轴点"]
        df_output.loc[index, f"{level}日经典支撑位1"] = c_points["支撑位1"]
        df_output.loc[index, f"{level}日斐波那契支撑位1"] = f_points["支撑位1"]
        df_output.loc[index, f"{level}日经典支撑位2"] = c_points["支撑位2"]
        df_output.loc[index, f"{level}日斐波那契支撑位2"] = f_points["支撑位2"]
        df_output.loc[index, f"{level}日经典支撑位3"] = c_points["支撑位3"]
        df_output.loc[index, f"{level}日斐波那契支撑位3"] = f_points["支撑位3"]
        df_output.loc[index, f"{level}日经典预期波动率1"] = c_points["预期波动率1"]
        df_output.loc[index, f"{level}日斐波那契预期波动率1"] = f_points["预期波动率1"]
        df_output.loc[index, f"{level}日经典预期波动率2"] = c_points["预期波动率2"]
        df_output.loc[index, f"{level}日斐波那契预期波动率2"] = f_points["预期波动率2"]
        df_output.loc[index, f"{level}日经典预期波动率3"] = c_points["预期波动率3"]
        df_output.loc[index, f"{level}日斐波那契预期波动率3"] = f_points["预期波动率3"]

    df_output = df_output.round(3)
    df_output.to_csv(f"docs/guide/latest.csv", index=False)
    df_output.to_csv(f"docs/guide/{today_str}.csv", index=False)
