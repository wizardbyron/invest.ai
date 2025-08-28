import streamlit as st

st.set_page_config(page_title="Invest.AI - 量化投资助手")
pages = {
    "Invest.AI": [
        st.Page("src/apps/individual.py",
                title="个股交易参考",
                icon=":material/explore:"),
        st.Page("src/apps/portfolio.py",
                title="投资组合参考",
                icon=":material/fact_check:"),
    ],
}

pg = st.navigation(pages)
pg.run()
