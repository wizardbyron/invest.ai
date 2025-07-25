import time

import streamlit as st
import pandas as pd

from src.strategy import pivot_points_grid
from src.util import nowstr

file = "./input/portfolio.csv"
df_portfolio = pd.read_csv(file, dtype={"代码": str, "名称": str})


with st.status("Loading...", expanded=False) as status:
    start_time = time.time()
    df = df_portfolio.copy()
    for index, row in df.iterrows():
        symbol = row["代码"]
        weekly = pivot_points_grid(symbol, 'weekly')
        daily = pivot_points_grid(symbol, 'daily')
        df.loc[index, "代码"] = f"single/?symbol={symbol}"
        df.loc[index, "当前价格"] = weekly["price"]
        df.loc[index, "Weekly建议"] = weekly["order"]
        df.loc[index, "Daily建议"] = daily["order"]

    end_time = time.time()
    duration = end_time - start_time
    msg = f"{nowstr()}分析完毕，用时{duration:.2f}秒"
    st.button("刷新", use_container_width=True)
    st.dataframe(df, height=900, column_config={
        "代码": st.column_config.LinkColumn(
            "代码",
            help="点击代码查看详情",
            max_chars=6,
            display_text=r"single/\?symbol=(.*)"
        ), }
    )
    status.update(label=msg, state="complete", expanded=True)
