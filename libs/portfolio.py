from datetime import datetime
from zoneinfo import ZoneInfo
import os

from langchain_community.document_loaders import DataFrameLoader
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd

from libs.utils.llm import create_chat
from libs.utils.tools import remove_leading_spaces, DISCLIAMER

timezone = ZoneInfo('Asia/Shanghai')


def portfolio_from_selected(type: str = "A股ETF", max_item: int = 10):
    llm_service = os.environ.get("LLM_SERVICE")
    model = os.environ.get("MODEL")
    df = pd.read_csv("input/selected.csv", dtype={'代码': str})

    if type == "全部":
        selected = df
    else:
        selected = df[df["类型"] == type]

    prompt = f"""以下是一份用于构建投资组合的候选股票或 ETF 清单：

    {selected.to_markdown(index=False)}

    从上述清单中帮我构建一份投资组合，要求如下：

    - 投资组合的股票或ETF 数量不超过 {max_item} 个
    - 采用杠铃型配置，兼顾风险和收益
    - A股，美股和港股在投资组合中均衡占比

    请以表格的方式输出投资组合，要求如下：

    - 股票或ETF名称及其代码
    - 股票或ETF在投资组合内的占比
    - 股票或ETF入选投资组合的原因
    - 股票或ETF的交易频率或者再平衡周期建议
    - 根据股票或ETF风险等级的低中高顺序输出
    - 输出未入选投资组合的股票或ETF以及未入选原因。

    并用以下格式输出每个股票或ETF的交易策略：

    ### 股票或 ETF 的名称（股票或 ETF 的代码）

    - 具体的交易策略，并解释交易策略
    - 交易频率

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

    chat = create_chat(llm_service, model)

    try:
        print(f"模型: {model}")

        response = chat.invoke(messages)

        output_md = f"""# A股ETF投资组合 - {chat.model_name}

        更新时间: {datetime.now(timezone).replace(microsecond=0)}

        模型: {chat.model_name}

        ## 投资组合参考

        {response.content}

        ## LLM 提示词

        {prompt}

        ## 免责声明

        {DISCLIAMER}
        """

        output_md = remove_leading_spaces(output_md)

        file_path = f"docs/portfolio/etf_{max_item}_{llm_service}.md"

        with open(file_path, 'w') as f:
            f.write(output_md)
    except Exception as e:
        print(f"调用模型[{chat.model_name}]失败:\n{e}")
