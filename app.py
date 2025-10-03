import streamlit as st

from src.apps.individual import individual_page
from src.util import disclaimer_text

page_title = "Invest.AI（演示版）"
st.set_page_config(page_title=page_title)
st.header(page_title)

pages = [
    st.Page(individual_page,
            title="首页",
            icon=":material/explore:")
]
pg = st.navigation(pages)
pg.run()
st.empty()
st.write(disclaimer_text)
st.write("© 2025 invest-ai.click All rights reserved.")
