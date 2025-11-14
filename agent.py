#!/usr/bin/env python

import fire
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from src.strategy import ai_guide
from src.util import nowstr, get_timezone_by_type, identify_stock_type


def guide(symbol: str, date: str) -> None:
    """获取交易指南

    Args:
        symbol (str): 代码 or ""
        series (str, optional): 基准价类型：经典/斐波那契/中值. Defaults to "斐波那契".

    Raises:
        ValueError: _description_
    """
    symbol = str(symbol).upper()
    timezone = ZoneInfo(get_timezone_by_type(identify_stock_type(symbol)))

    if date is None:
        end_date = datetime.now(timezone)
    else:
        end_date = datetime.strptime(str(date), '%Y%m%d')
    print(ai_guide(symbol, end_date.strftime('%Y-%m-%d')))


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(guide)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")
