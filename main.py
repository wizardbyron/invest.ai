import fire

from libs.backtest import backtest
from libs.guide import guide
from libs.portfolio import create_portfolio


def main_hello(program):
    if program:
        if program == 'portfolio':
            create_portfolio()
        elif program == 'guide':
            guide()
        elif program == 'backtest':
            backtest()


if __name__ == "__main__":
    fire.Fire(main_hello)
