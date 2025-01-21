import time

import fire

from libs.backtest import backtest
from libs.guide import guide
from libs.portfolio import create_portfolio


def main_hello(program):
    start_time = time.time()

    if program:
        if program == 'portfolio':
            create_portfolio()
        elif program == 'guide':
            guide()
        elif program == 'backtest':
            backtest()
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")


if __name__ == "__main__":
    fire.Fire(main_hello)
