import time

import streamlit as st
import pandas as pd

from src.strategy import pivot_points_grid
from src.util import nowstr, format_for_markdown, disclaimer_md

portfolios = {
    '基础-5': 'basic_5',
    '基础-10': 'basic_10',
    '调和-5': 'blended_5',
    '调和-10': 'blended_10',
    '躺平-5': 'layflat_5',
    '躺平-10': 'layflat_10',
    '默认': 'all',
}

option = st.selectbox("投资组合", portfolios.keys())

file = f"./input/portfolios/{portfolios[option]}.csv"
df_portfolio = pd.read_csv(file, dtype={"代码": str, "名称": str})
with st.status("分析中...", expanded=False) as status:
    start_time = time.time()
    df = df_portfolio.copy()
    for index, row in df.iterrows():
        symbol = row["代码"]
        weekly = pivot_points_grid(symbol, 'weekly')
        daily = pivot_points_grid(symbol, 'daily')
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
    st.markdown(disclaimer_md())
    status.update(label=msg, state="complete", expanded=True)
