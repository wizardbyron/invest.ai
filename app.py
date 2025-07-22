import streamlit as st

from src.strategy import pivot_points_grid

col_symbol, col_button = st.columns([3, 1],  vertical_alignment="bottom")

symbol = col_symbol.text_input("Symbol")

if col_button.button('分析', use_container_width=True) and len(symbol) >= 3:
    with st.status("Loading...", expanded=False) as status:
        col_daily, col_weekly = st.columns([2, 2])

        resp_daily = pivot_points_grid(symbol, "daily")
        col_daily.caption("Daily")
        col_daily.dataframe(resp_daily['merged_table'], height=700)
        col_daily.caption(resp_daily['message'])

        resp_weekly = pivot_points_grid(symbol, "weekly")
        col_weekly.caption("Weekly")
        col_weekly.dataframe(resp_weekly['merged_table'], height=700)
        col_weekly.caption(resp_weekly['message'])
        status.update(label="Done", state="complete", expanded=True)
