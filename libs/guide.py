from datetime import datetime, timedelta

import akshare as ak
import pandas as pd
from libs.utils.indicators import fibonacci, classic
from libs.utils.data import fetch_klines

disclaimer = "本站用于实验目的，不构成任何投资建议，也不作为任何法律法规、监管政策的依据，\
    投资者不应以该等信息作为决策依据或依赖该等信息做出法律行为，由此造成的一切后果由投资者自行承担。"


def guide():

    level = 5
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
        market, history_klines = fetch_klines(
            type=type,
            symbol=symbol,
            start_date=start_date_str,
            end_date=today_str)

        # 获取上周的交易数据
        if today.weekday() < 5 and today.weekday() > 0:  # 交易日
            off_day = today.weekday()
            if history_klines["日期"].iloc[-1] == today.strftime("%Y-%m-%d"):
                off_day += 1  # 当天收盘后，去掉当天数据
            df = history_klines[-level-off_day:-off_day]
        else:  # 周末
            df = history_klines[-level:]

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

        更新日期: {today.strftime("%Y-%m-%d")}

        ## 5日枢轴点

        取值日期区间: {start_date} 至 {end_date}

        {df_single.round(3).to_markdown()}

        ## 免责声明

        {disclaimer}

        """.replace(" "*8, "")

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