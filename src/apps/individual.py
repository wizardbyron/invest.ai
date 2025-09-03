import streamlit as st

from src.data import get_stock_name
from src.strategy import pivot_points_grid
from src.util import nowstr


def pivot_df(st: st, symbol: str, period: str):
    resp = pivot_points_grid(symbol, period)
    resp['merged_table'] = resp['merged_table'].rename_axis(f'{period}交易')
    price = resp['price']
    name = get_stock_name(symbol)
    if resp['order'] == '买入':
        st.badge(f"{price}元-买入-{name}",
                 color="red",
                 icon=":material/input:")
    elif resp['order'] == '卖出':
        st.badge(f"{price}元-卖出-{name}",
                 color="green",
                 icon=":material/output:")
    else:
        st.badge(f"{price}元-观望-{name}",
                 color="blue",
                 icon=":material/pending:")
    st.table(resp['merged_table'])


if st.query_params == {}:
    symbol = st.text_input("请输入股票代码：(支持A股、港股、美股以及ETF)", max_chars=6)
else:
    symbol = st.text_input("请输入股票代码：(支持A股、港股、美股以及ETF)", max_chars=6,
                           value=st.query_params["symbol"])

if len(symbol) >= 3:
    with st.status("分析中...", expanded=False) as status:
        st.button(f"立即更新", use_container_width=True)
        col_weekly, col_daily = st.columns([2, 2])

        pivot_df(col_weekly, symbol, "weekly")
        pivot_df(col_daily, symbol, "daily")

        status.update(label=f"{nowstr()}分析完毕，交易参考如下",
                      state="complete",
                      expanded=True)
