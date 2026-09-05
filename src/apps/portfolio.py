import time
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

from src.strategy import pivot_points_grid
from src.util import nowstr, format_for_markdown, disclaimer_text


def portfolio_tab():
    portfolios = {
        '实盘持仓': 'holdings',
        '默认': 'all',
        '股票': 'stocks',
        '红利': 'dividend',
    }

    option = st.selectbox("投资组合", portfolios.keys())

    file = f"./input/portfolios/{portfolios[option]}.csv"
    df_portfolio = pd.read_csv(file, dtype={"代码": str, "名称": str})

    # 日期窗口：近15个自然日的周K/日K，取前一交易日为枢轴基准
    today = st.date_input(
        "基准日期（默认今天，用前一交易日K线计算）",
        max_value="today",
        format="YYYY-MM-DD",
        value="today")
    end_date = today.strftime("%Y-%m-%d")
    start_date = (today - timedelta(days=15)).strftime("%Y-%m-%d")
    point_type = st.selectbox("枢轴类型", ['斐波那契', '经典', '卡玛利拉'], index=0)

    with st.status("分析中...", expanded=False) as status:
        start_time = time.time()
        df = df_portfolio.copy()
        for index, row in df.iterrows():
            symbol = row["代码"]
            weekly = pivot_points_grid(symbol, 'weekly', start_date, end_date, point_type)
            daily = pivot_points_grid(symbol, 'daily', start_date, end_date, point_type)
            df.loc[index, "代码"] = f"[{symbol}](/?symbol={symbol})"
            df.loc[index, "当前价格"] = weekly["price"]
            df.loc[index, "周建议"] = format_for_markdown(weekly["order"])
            df.loc[index, "日建议"] = format_for_markdown(daily["order"])

        end_time = time.time()
        duration = end_time - start_time
        df = df.set_index("代码")
        msg = f"{nowstr()}分析完毕，用时{duration:.2f}秒"
        st.button("立即更新", use_container_width=True)
        st.table(df)
        st.markdown(f"---\n{disclaimer_text}")
        status.update(label=msg, state="complete", expanded=True)
