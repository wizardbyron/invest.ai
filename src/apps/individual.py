import streamlit as st

from src.data import get_stock_name
from src.strategy import pivot_points_grid, ai_guide
from src.util import nowstr, todaystr


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


def individual_page():
    hint = "请输入股票代码用于演示(支持A股、港股、美股以及ETF)"
    if st.query_params == {}:
        symbol = st.text_input(hint, max_chars=6)
    else:
        symbol = st.text_input(hint, max_chars=6,
                               value=st.query_params["symbol"])

    if len(symbol) >= 3:
        with st.status("分析中...", expanded=False) as status:
            record_file = f'./record/{symbol.upper()}_{todaystr()}.md'
            try:
                # col_weekly, col_daily = st.columns([2, 2])
                # pivot_df(col_weekly, symbol, "weekly")
                # pivot_df(col_daily, symbol, "daily")

                status.update(label=f"读取 AI 分析报告",
                              state="running",
                              expanded=True)
                with open(record_file, 'r') as f:
                    st.markdown(f.read())
                status.update(label=f"完成",
                              state="complete",
                              expanded=True)
            except FileNotFoundError as e:
                status.update(label=f"AI 分析中，请稍后...",
                              state="running",
                              expanded=True)
                resp = ai_guide(symbol, todaystr())
                st.markdown(resp)
                with open(record_file, 'w') as f:
                    f.write(resp)
                status.update(label=f"{nowstr()} 分析完成",
                              state="complete",
                              expanded=True)
            except Exception as e:
                status.update(label=f"{nowstr()} - 系统错误",
                              state="complete",
                              expanded=True)
                st.error('系统错误，请稍后再试。')
                print(e)
            #
