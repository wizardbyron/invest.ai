import streamlit as st
from src.apps.individual import individual_tabs

page_title = "Invest.AI（内测版）"
st.set_page_config(page_title=page_title)
st.subheader(page_title, divider="gray")
individual_tabs()
st.write("© 2025 invest-ai.click All rights reserved.")
