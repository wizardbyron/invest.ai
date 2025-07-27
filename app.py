import streamlit as st


pages = {
    "Invest.AI": [
        st.Page("src/apps/single.py",
                title="个股指南",
                icon=":material/explore:"),
        st.Page("src/apps/portfolio.py",
                title="投资组合",
                icon=":material/fact_check:"),
    ],
}

pg = st.navigation(pages)
pg.run()
