import re
import time

import fire
import pandas as pd
from tqdm import tqdm

from src.agents import trade_agent
from src.util import todaystr, nowstr, todaystr_zh
from pathlib import Path


def extract_trade_info(output: str, symbol: str) -> dict:
    """从交易指南输出中提取关键信息"""
    lines = output.split("\n")

    stock_name = ""
    trade_suggestion = ""
    buy_range = ""
    sell_range = ""

    # 提取股票名称
    title_match = re.search(r"# ([\w\d]+)-(.+)", lines[0])
    if title_match:
        stock_name = title_match.group(2).strip()

    # 解析内容
    section = ""
    for i, line in enumerate(lines):
        line = line.strip()

        if line.startswith("### 交易建议："):
            section = "suggestion"
            continue
        elif line.startswith("### 交易价格："):
            section = "price"
            continue
        elif line.startswith("### 原因说明："):
            section = "reason"
            continue
        elif line.startswith("## 交易参考"):
            break

        if section == "suggestion" and line and not line.startswith("#"):
            trade_suggestion = line
        elif section == "price" and line and not line.startswith("#"):
            # 解析买入和卖出价格区间
            if "买入" in line or "Buy" in line or "buy" in line:
                buy_range = line
            elif "卖出" in line or "Sell" in line or "sell" in line:
                sell_range = line

    return {
        "symbol": symbol,
        "name": stock_name,
        "trade_suggestion": trade_suggestion,
        "buy_range": buy_range,
        "sell_range": sell_range,
    }


def make_trade_guides(portfolio: str = "all", date: str = ""):
    start_time = time.time()
    if date == "":
        date = todaystr()

    file_path = f"./input/portfolios/{portfolio}.csv"
    path_str = f"./docs/交易指南/{todaystr_zh()}"
    dir_path = Path(path_str)

    trade_data_list = []

    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"目录 '{dir_path}' 创建成功或已存在")

        df_portfolio = pd.read_csv(file_path, dtype={"代码": str, "名称": str})
        symbols = df_portfolio["代码"].values

        print(f"分析日期:{date}，分析进度")

        for symbol in tqdm(symbols, leave=False):
            try:
                output = trade_agent(symbol, date)
                filename = f"{path_str}/{symbol}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(output)

                trade_info = extract_trade_info(output, symbol)
                trade_data_list.append(trade_info)
            except Exception as e:
                print(f"处理{symbol}时发生错误：{str(e)}")

        # 生成汇总文档
        summary_path = f"{path_str}/0-交易指南汇总.md"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"# 交易指南汇总\n\n")
            f.write(f"> 生成时间: {nowstr()}\n\n")

            # 按交易建议分组
            buy_stocks = []
            sell_stocks = []
            hold_stocks = []

            for data in trade_data_list:
                suggestion = data["trade_suggestion"]
                if "买入" in suggestion:
                    buy_stocks.append(data)
                elif "卖出" in suggestion:
                    sell_stocks.append(data)
                else:
                    hold_stocks.append(data)

            # 买入股票
            if buy_stocks:
                f.write(f"## 买入\n\n")
                f.write(f"| 股票代码 | 股票名称 | 买入价格区间 | 卖出价格区间 |\n")
                f.write(f"|---------|---------|-------------|-------------|\n")
                for data in buy_stocks:
                    f.write(
                        f"| [{data['symbol']}]({data['symbol']}.md) | [{data['name']}]({data['symbol']}.md) | {data['buy_range']} | {data['sell_range']} |\n"
                    )
                f.write(f"\n")

            # 卖出股票
            if sell_stocks:
                f.write(f"## 卖出\n\n")
                f.write(f"| 股票代码 | 股票名称 | 买入价格区间 | 卖出价格区间 |\n")
                f.write(f"|---------|---------|-------------|-------------|\n")
                for data in sell_stocks:
                    f.write(
                        f"| [{data['symbol']}]({data['symbol']}.md) | [{data['name']}]({data['symbol']}.md) | {data['buy_range']} | {data['sell_range']} |\n"
                    )
                f.write(f"\n")

            # 观望股票
            if hold_stocks:
                f.write(f"## 观望\n\n")
                f.write(f"| 股票代码 | 股票名称 | 买入价格区间 | 卖出价格区间 |\n")
                f.write(f"|---------|---------|-------------|-------------|\n")
                for data in hold_stocks:
                    f.write(
                        f"| [{data['symbol']}]({data['symbol']}.md) | [{data['name']}]({data['symbol']}.md) | {data['buy_range']} | {data['sell_range']} |\n"
                    )
                f.write(f"\n")

        print(f"汇总文档已生成: {summary_path}")
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
    except OSError as e:
        print(f"创建目录失败: {e}")

    end_time = time.time()
    duration = end_time - start_time
    print(f"[{nowstr()} 执行完成, 花费:{duration:.2f}秒]")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(make_trade_guides)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
