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
    return df


daily_table=None
weekly_table= None
def show_stock_data():
    global daily_table
    global weekly_table
    stock_code = input_code.value
    if len(stock_code)>=5:
        df_daily = get_points(stock_code, "daily")
        df_weekly = get_points(stock_code, "weekly")
        
        with ui.row():
            if weekly_table is None or daily_table is None:
                daily_table = ui.table.from_pandas(df_daily,title="今日枢轴点")
                weekly_table = ui.table.from_pandas(df_weekly,title="本周枢轴点")
            else:
                ui.table.update_from_pandas(daily_table, df_daily)
                ui.table.update_from_pandas(weekly_table, df_weekly)
                print("更新表格:"+nowstr())        
                

ui.page_title('Invest.AI')
ui.dark_mode().enable()
ui.timer(5.0, lambda: show_stock_data())

with ui.header() as header:
    ui.icon('add_chart').classes('text-3xl')
    ui.label('Invest.AI').classes('text-xl text-bold')

with ui.row():
    input_code = ui.input(placeholder='股票代码').props('outlined dense')
    ui.button('update', on_click=show_stock_data)
    ui.separator()

with ui.footer() as footer:
    ui.label('Invest.AI © 2025')


ui.run()
    