import streamlit as st

from src.strategy import pivot_points_grid
from src.util import nowstr


def pivot_df(st: st, symbol: str, period: str):
    resp_weekly = pivot_points_grid(symbol, period)
    if resp_weekly['order'] == '买入':
        st.badge(f"{period}-买入", color="red")
    elif resp_weekly['order'] == '卖出':
        st.badge(f"{period}-卖出", color="green")
    else:
        st.badge(f"{period}-观望", color="blue")
    st.dataframe(resp_weekly['merged_table'], height=700)


symbol = st.text_input("请输入股票代码", max_chars=6)
if st.button('分析', use_container_width=True) and len(symbol) >= 3:
    with st.status("Loading...", expanded=False) as status:
        col_weekly, col_daily = st.columns([2, 2])

        pivot_df(col_weekly, symbol, "weekly")
        pivot_df(col_daily, symbol, "daily")

        status.update(label=f"{nowstr()}分析完毕，结果如下",
                      state="complete",
                      expanded=True)
