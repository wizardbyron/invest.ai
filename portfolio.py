import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo

import fire
import pandas as pd

from langchain_core.messages import HumanMessage, SystemMessage

from src.util.llm import create_chat
from src.util.tools import remove_leading_spaces, append_discliamer

timezone = ZoneInfo('Asia/Shanghai')
now = datetime.now(timezone)
now_str = now.strftime("%Y-%m-%d %H:%M:%S")

llm_list = [
    ("zhipuai", "glm-4-plus"),
    ("deepseek", "deepseek-reasoner"),
    ("ollama", "glm4"),
    ("moonshot", "moonshot-v1-128k")
]


def selected(type: str = 'A股ETF', max: int = 10) -> str:

    df = pd.read_csv("input/selected.csv", dtype={'代码': str})

    selected = df[df["类型"] == type]

    prompt = f"""以下是一份用于构建投资组合的{type}清单：

    {selected.to_markdown(index=False)}

    从上述清单中帮我构建一份投资组合，要求如下：

    - 投资组合的 {type} 数量为 {max} 个
    - 采用杠铃型配置，兼顾风险和收益
    - A股占比 40%, 美国市场标的占比 30%, 香港市场标的占比 30%

    请输出投资组合，要求如下：

    - {type}名称及其代码, 以及在投资组合内的占比
    - 入选投资组合的原因
    - 交易频率或者再平衡周期建议
    - 根据风险等级的低中高顺序输出

    并用以下格式输出每个{type}的交易策略：

    ## 风险等级

    ### {type} 的名称（{type}的交易代码）

    - 在投资组合内的占比
    - 入选投资组合的原因
    - 具体的交易策略，并解释交易策略
    - 交易频率

    ## 投资组合交易策略
    """

    prompt = remove_leading_spaces(prompt)

    print(prompt)

    messages = [
        SystemMessage(
            content="你是一个专业的投资人，可以根据我所给出的投资标的编制出投资组合，做到风险和收益兼顾。"
        ),
        HumanMessage(
            content=prompt
        )
    ]

    for llm_service, model in llm_list:
        chat = create_chat(llm_service, model)

        try:
            print(f"模型: {model}")

            response = chat.invoke(messages)

            output_md = f"""# A股ETF投资组合 - {llm_service}

            更新时间: {now_str}

            模型: {model}

            ## 投资组合参考

            {response.content}

            ## LLM 提示词

            {prompt}
            """
            output_md = append_discliamer(output_md)
            output_md = remove_leading_spaces(output_md)

            file_path = f"docs/投资组合/自选{type}投资组合_{llm_service}.md"

            with open(file_path, "w") as f:
                f.write(output_md)

        except Exception as e:
            print(f"调用模型[{model}]失败:\n{e}")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire()
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
