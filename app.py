import streamlit as st
from src.apps.individual import individual_tabs
from src.apps.portfolio import portfolio_tab

page_title = "Invest.AI（内测版）"
st.set_page_config(page_title=page_title)
st.subheader(page_title, divider="gray")

tab_individual, tab_portfolio = st.tabs(["个股交易参考", "投资组合工作台"])

with tab_individual:
    individual_tabs()

with tab_portfolio:
    portfolio_tab()

st.write("© 2025 invest-ai.click All rights reserved.")
