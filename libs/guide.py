from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from libs.utils.data import history_klines
from libs.utils.indicators import fibonacci, classic
from libs.utils.tools import remove_leading_spaces, DISCLIAMER

timezone = ZoneInfo('Asia/Shanghai')


def weekly_pivot_points():
    now_str = datetime.now(timezone).strftime("%Y%m%d  %H:%M:%S")
    today = datetime.today()
    today_str = today.strftime("%Y%m%d")
    start_date = today - timedelta(days=100)
    start_date_str = start_date.strftime("%Y%m%d")

    df_input = pd.read_csv("input/selected.csv", dtype={"代码": str})
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
        if (today.weekday() < 5):  # 周内
            df_last_week = df_weekly[-2:-1]
        else:  # 周末
            df_last_week = df_weekly[-1:]

        print(df_last_week)

        start_date = df_last_week["日期"].iloc[0]
        end_date = df_last_week["日期"].iloc[-1]
        high = df_last_week["最高"].max()
        low = df_last_week["最低"].min()
        close = df_last_week["收盘"].iloc[-1]

        c_points = classic(high, low, close)
        f_points = fibonacci(high, low, close)

        item = {"经典": c_points, "斐波那契": f_points}
        row_index = c_points.keys()
        df_single = pd.DataFrame(item, index=row_index)
        df_single["中间值"] = (df_single["经典"] + df_single["斐波那契"])/2
        df_single = df_single.round(3)

        output_md = f"""# {symbol} - {name}

        更新时间: {now_str}

        ## 交易参考

        ### 周线枢轴点 ({end_date})

        {df_single.to_markdown()}

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
