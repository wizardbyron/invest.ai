import time

import pandas as pd
from tqdm import tqdm

from src.agents import trade_agent
from src.util import todaystr, nowstr


if __name__ == "__main__":
    # 使用示例
    start_time = time.time()
    file_path = "./input/portfolios/all.csv"  # 替换为你的CSV文件路径
    try:
        df_portfolio = pd.read_csv(file_path, dtype={"代码": str, "名称": str})
        symbols = df_portfolio["代码"].values
        date = todaystr()
        print(f'分析日期:{date}，分析进度')

        for symbol in tqdm(symbols, leave=False):
            try:
                output = trade_agent(symbol, date)
                filename = f"./record/{symbol}_{date}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(output)
            except Exception as e:
                print(f"处理{symbol}时发生错误：{str(e)}")

    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")

    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")
