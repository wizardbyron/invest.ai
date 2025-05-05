#!/usr/bin/env python
from nicegui import ui

from src.data import history_klines
from src.indicators import pivot_points_table, merge_points
from src.strategy import pivot_points_grid
from src.util import nowstr

def get_points(stock_code: str, period: str):
    tzone, klines = history_klines(stock_code, period)
    points = pivot_points_table(klines[-2:-1])
    df = merge_points(klines.iloc[-1], points)
    df.index.name = "参考点位"
    df = df.reset_index()
    return tzone,df


daily_table=None
weekly_table= None
def update_tables():
    global daily_table
    global weekly_table
    stock_code = input_code.value
    if stock_code.strip() != "" :
        tzone,df_daily = get_points(stock_code, "daily")
        tzone,df_weekly = get_points(stock_code, "weekly")
        ui.notify(f"{stock_code}数据更新时间：{nowstr(tzone)}")
        with ui.row():
            if weekly_table is None or daily_table is None:
                daily_table = ui.table.from_pandas(df_daily,title=f"日内交易参考")
                weekly_table = ui.table.from_pandas(df_weekly,title="本周交易参考")

            else:
                ui.table.update_from_pandas(daily_table, df_daily)
                ui.table.update_from_pandas(weekly_table, df_weekly)

                

ui.page_title('Invest.AI')
ui.dark_mode().enable()
ui.timer(10.0, lambda: update_tables())

with ui.header() as header:
    ui.icon('add_chart').classes('text-3xl')
    ui.label('Invest.AI').classes('text-xl text-bold')


with ui.row():
    input_code = ui.input(placeholder='股票代码').props('outlined dense')
    ui.button('update', on_click=update_tables)
    ui.separator()

with ui.footer() as footer:
    ui.label('Invest.AI © 2025')


ui.run()
    