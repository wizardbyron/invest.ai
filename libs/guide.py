from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from libs.utils.data import history_klines
from libs.utils.indicators import pivot_points
from libs.utils.tools import remove_leading_spaces, DISCLIAMER

timezone = ZoneInfo('Asia/Shanghai')


def weekly_pivot_points():
    now_str = datetime.now(timezone).strftime("%Y-%m-%d  %H:%M:%S")
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
        if (today.weekday() < 5 and today.weekday() > 0):  # 周内
            df_last_week = df_weekly[-2:-1]
        else:  # 周末
            df_last_week = df_weekly[-1:]

        print(df_last_week)

        start_date = df_last_week["日期"].iloc[0]
        end_date = df_last_week["日期"].iloc[-1]
        df_single = pivot_points(df_last_week)

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
