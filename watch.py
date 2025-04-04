#!/usr/bin/env python
import fire
import time

from guide import guide

from src.util.tools import is_trading_time


def watch(market: str, symbol: str):
    while (is_trading_time('Asia/Shanghai')):
        guide(market, symbol)
        time.sleep(10)


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(watch)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[运行时间：{duration:.2f}秒]")
