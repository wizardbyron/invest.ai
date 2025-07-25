import streamlit as st


pages = {
    "Invest.AI": [
        st.Page("src/apps/portfolio.py", title="投资组合"),
        st.Page("src/apps/single.py", title="个股分析"),
    ],
}

pg = st.navigation(pages)
pg.run()
