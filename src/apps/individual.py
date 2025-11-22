
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from src.agents import trade_agent
from src.util import nowstr
from src.data import get_stock_name
from src.strategy import pivot_points_grid
from src.util import nowstr, get_timezone_by_type


def pivot_df(st: st, symbol: str, period: str, end_date: str, point_type: str):

    timezone = ZoneInfo(get_timezone_by_type(symbol))
    now = datetime.now(timezone)
    start_date = (now - timedelta(days=15)).strftime('%Y-%m-%d')

    resp = pivot_points_grid(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        point_type=point_type
    )

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


def individual_table(symbol: str, date: datetime, option: str = '斐波那契'):
    if st.button("价格分析", use_container_width=True) and len(symbol) >= 3:
        with st.status("分析中...", expanded=False) as status:
            col_weekly, col_daily = st.columns([2, 2])
            pivot_df(st=col_weekly,
                     symbol=symbol,
                     period="weekly",
                     end_date=date.strftime("%Y-%m-%d"),
                     point_type=option)
            pivot_df(st=col_daily,
                     symbol=symbol,
                     period="daily",
                     end_date=date.strftime("%Y-%m-%d"),
                     point_type=option)
            status.update(label=f"{nowstr()} 分析完毕，{date}交易参考如下",
                          state="complete",
                          expanded=True)


def individual_ai(symbol: str, date: datetime):
    if st.button("AI 分析", use_container_width=True) and len(symbol) >= 3:
        with st.status("分析中...", expanded=False) as status:
            record_file = f'./record/{symbol.upper()}_{date.strftime("%Y%m%d")}.md'
            try:
                status.update(label=f"{nowstr()} 读取 AI 分析报告",
                              state="running",
                              expanded=False)
                with open(record_file, 'r') as f:
                    st.markdown(f.read())
                status.update(label=f"{nowstr()} 读取 AI 分析报告完成",
                              state="complete",
                              expanded=True)
            except FileNotFoundError as e:
                status.update(label=f"AI 分析中，请稍后...",
                              state="running",
                              expanded=False)
                resp = trade_agent(symbol=symbol,
                                   end_date=date.strftime("%Y-%m-%d"))
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
                st.error(f"系统错误: {e}")


def individual_tabs():
    left, right = st.columns(2)

    with left:
        symbol_help = f"仅支持输入代码，不支持输入名称。支持A股，港股，美股及ETF。"
        symbol = st.text_input("股票代码", max_chars=6, help=symbol_help).upper()

    with right:
        end_date = st.date_input(
            "请选择日期，默认为今天",
            max_value="today",
            format="YYYY-MM-DD",
            value="today")

    individual_ai(symbol, end_date)

    # ai, table = st.tabs(["AI 分析","交易价格参考"])

    # with ai:
    #     individual_ai(symbol, end_date)

    # with table:
    #     individual_table(symbol, end_date)
