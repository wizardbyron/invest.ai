#!/usr/bin/env python3

import fire
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from src.agents import trade_agent
from src.util import nowstr, get_timezone_by_type, identify_stock_type


def agent(symbol: str, date: str = "") -> None:
    """获取交易指南

    Args:
        symbol (str): 代码 or ""
        series (str, optional): 基准价类型：经典/斐波那契/中值. Defaults to "斐波那契".

    Raises:
        ValueError: _description_
    """
    symbol = str(symbol).upper()
    timezone = ZoneInfo(get_timezone_by_type(identify_stock_type(symbol)))

    if date == "":
        end_date = datetime.now(timezone)
    else:
        end_date = datetime.strptime(str(date), '%Y%m%d')
    resp = trade_agent(symbol, end_date.strftime('%Y-%m-%d'))
    print(resp)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(agent)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")
