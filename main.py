from datetime import datetime, timedelta
import time

import fire

from libs.backtest import run_backtest
from libs.guide import weekly_pivot_points
from libs.guide_ai import ai_guide
from libs.portfolio import portfolio_from_selected


today = datetime.today()
today_str = today.strftime('%Y%m%d')
same_day_last_year = today - timedelta(days=365)
same_day_last_year_str = same_day_last_year.strftime('%Y%m%d')


def portfolio(num=10):
    print(f'投资组合数量: {num}\n')
    portfolio_from_selected("A股ETF", num)


def guide():
    weekly_pivot_points()


def guide_ai():
    ai_guide()


def backtest(start_date=same_day_last_year_str, end_date=today_str):
    print(f'回测日期: {start_date} 至 {end_date}\n')
    run_backtest(start_date, end_date)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire()
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
