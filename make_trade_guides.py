import time

import fire
import pandas as pd
from tqdm import tqdm

from src.agents import trade_agent
from src.util import todaystr, nowstr, todaystr_zh
from pathlib import Path


def make_trade_guides(date=""):
    # 使用示例
    start_time = time.time()
    if date == "":
        date = todaystr()

    file_path = "./input/portfolios/all.csv"  # 替换为你的CSV文件路径
    path_str = f'./docs/交易指南/{todaystr_zh()}'
    dir_path = Path(path_str)
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"目录 '{dir_path}' 创建成功或已存在")

        df_portfolio = pd.read_csv(file_path, dtype={"代码": str, "名称": str})
        symbols = df_portfolio["代码"].values

        print(f'分析日期:{date}，分析进度')

        for symbol in tqdm(symbols, leave=False):
            try:
                output = trade_agent(symbol, date)
                filename = f"{path_str}/{symbol}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(output)
            except Exception as e:
                print(f"处理{symbol}时发生错误：{str(e)}")
    except OSError as e:
        print(f"创建目录失败: {e}")
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")

    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(make_trade_guides)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
