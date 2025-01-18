import os
from datetime import datetime, timedelta

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage

from libs.utils.chat_model import chat_models
from libs.utils.data import fetch_klines
from libs.utils.indicators import fibonacci, classic
from libs.utils.tools import remove_leading_spaces

disclaimer = """本站用于实验目的，不构成任何投资建议，也不作为任何法律法规、监管政策的依据，投资者不应以该等信息作为决策依据或依赖该等信息做出法律行为，由此造成的一切后果由投资者自行承担。"""

output_format_prompt = """输出格式如下：

### 交易建议

### 交易价格

### 交易分析
"""


def guide():

    level = 5
    today = datetime.today()
    today_str = today.strftime("%Y%m%d")
    start_date = today - timedelta(days=100)
    start_date_str = start_date.strftime("%Y%m%d")
    model = os.environ.get('MODEL', 'glm4')
    chat_model = chat_models[model]

    df_input = pd.read_csv("input/selected.csv", dtype={"代码": str})
    df_output = df_input.copy()
    for index, row in df_input.iterrows():
        print(row)

        type = row["类型"]
        symbol = row["代码"]
        name = row["名称"]
        market, history_klines = fetch_klines(
            type=type,
            symbol=symbol,
            start_date=start_date_str,
            end_date=today_str)

        # 获取上周的交易数据
        if today.weekday() < 5 and today.weekday() > 0:  # 交易日
            off_day = today.weekday()
            if history_klines["日期"].iloc[-1] == today.strftime("%Y-%m-%d"):
                off_day += 1  # 当天收盘后，去掉当天数据
            df = history_klines[-level-off_day:-off_day]
        else:  # 周末
            df = history_klines[-level:]

        # print(df)

        start_date = df["日期"].iloc[0]
        end_date = df["日期"].iloc[-1]
        high = df["最高"].max()
        low = df["最低"].min()
        close = df["收盘"].iloc[-1]

        c_points = classic(high, low, close)
        f_points = fibonacci(high, low, close)

        item = {"经典": c_points, "斐波那契": f_points}
        row_index = c_points.keys()
        df_single = pd.DataFrame(item, index=row_index)
        df_single["中间值"] = (df_single["经典"] + df_single["斐波那契"])/2

        prompt = f"""以下是 {name} 过去 30 个交易日的 K 线数据：

        {history_klines[-30:].to_markdown(index=False)}

        以下是 {name} 上一周的枢轴点数据。计算起止时间为 {start_date} 至 {end_date}

        {df_single.round(3).to_markdown(index=False)}

        以下是 {name} 的均线数据：

        * 5 日均线: {history_klines["收盘"][-5:].mean():.3f}
        * 10 日均线: {history_klines["收盘"][-10:].mean():.3f}
        * 20 日均线: {history_klines["收盘"][-20:].mean():.3f}
        * 30 日均线: {history_klines["收盘"][-30:].mean():.3f}

        请根据以上数据给出股票交易建议，交易策略如下：

        - 买入点在支撑位上
        - 卖出点在阻力位上
        - 如果当前价格下跌低于支撑位，则考虑下一个支撑位的价格，包括中间值
        - 如果当前价格上涨高于阻力位，则考虑下一个阻力位的价格，包括中间值

        输出要求如下：

        - 输出增持，减持，观望三者建议之一，并说明原因
        - 如果是增持或者减持，则需要给出交易价格
        - 不考虑预期波动率的影响
        """

        prompt = remove_leading_spaces(prompt)

        print(prompt)

        messages = [
            SystemMessage(
                content="你是一个专业的股票交易员，你可以根据股票的各项指标给出最佳交易建议。"
            ),
            HumanMessage(
                content=prompt + output_format_prompt
            )
        ]

        response = chat_model.invoke(messages)

        output_md = f"""# {symbol} - {name}

        更新日期: {today.strftime("%Y-%m-%d")}

        ## 交易建议

        AI 模型: {chat_model.model_name}

        {response.content}

        ## 参考

        ### 最近一个交易日的数据

        {history_klines.iloc[-1].to_markdown()}

        ### 提示词

        {prompt}

        ## 免责声明

        {disclaimer}

        """

        output_md = remove_leading_spaces(output_md)

        file_path = f"docs/guide/{market}/{symbol}.md"

        with open(file_path, "w") as f:
            f.write(output_md)

        df_output.loc[index, f"{level}日经典阻力位3"] = c_points["阻力位3"]
        df_output.loc[index, f"{level}日斐波那契阻力位3"] = f_points["阻力位3"]
        df_output.loc[index, f"{level}日经典阻力位2"] = c_points["阻力位2"]
        df_output.loc[index, f"{level}日斐波那契阻力位2"] = f_points["阻力位2"]
        df_output.loc[index, f"{level}日经典阻力位1"] = c_points["阻力位1"]
        df_output.loc[index, f"{level}日斐波那契阻力位1"] = f_points["阻力位1"]
        df_output.loc[index, f"{level}日枢轴点"] = c_points["枢轴点"]
        df_output.loc[index, f"{level}日经典支撑位1"] = c_points["支撑位1"]
        df_output.loc[index, f"{level}日斐波那契支撑位1"] = f_points["支撑位1"]
        df_output.loc[index, f"{level}日经典支撑位2"] = c_points["支撑位2"]
        df_output.loc[index, f"{level}日斐波那契支撑位2"] = f_points["支撑位2"]
        df_output.loc[index, f"{level}日经典支撑位3"] = c_points["支撑位3"]
        df_output.loc[index, f"{level}日斐波那契支撑位3"] = f_points["支撑位3"]
        df_output.loc[index, f"{level}日经典预期波动率1"] = c_points["预期波动率1"]
        df_output.loc[index, f"{level}日斐波那契预期波动率1"] = f_points["预期波动率1"]
        df_output.loc[index, f"{level}日经典预期波动率2"] = c_points["预期波动率2"]
        df_output.loc[index, f"{level}日斐波那契预期波动率2"] = f_points["预期波动率2"]
        df_output.loc[index, f"{level}日经典预期波动率3"] = c_points["预期波动率3"]
        df_output.loc[index, f"{level}日斐波那契预期波动率3"] = f_points["预期波动率3"]

    df_output = df_output.round(3)
    df_output.to_csv(f"docs/guide/latest.csv", index=False)
    df_output.to_csv(f"docs/guide/{today_str}.csv", index=False)
