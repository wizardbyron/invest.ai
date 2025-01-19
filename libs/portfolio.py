from datetime import datetime
from langchain_community.document_loaders import DataFrameLoader
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd

from libs.utils.chat_model import chat_models
from libs.utils.tools import remove_leading_spaces, DISCLIAMER


def create_portfolio():
    df = pd.read_csv("input/selected.csv", dtype={'代码': str})

    etf_cn = df[df["类型"] == "A股ETF"]

    loader = DataFrameLoader(etf_cn, page_content_column="名称")

    docs = loader.load()

    num = 10

    prompt = f"""以下是一份用于构建投资组合的候选股票清单：

    {docs}

    从上述候选股票清单中帮我构建一份投资组合，要求如下：

    - 投资组合的股票数量为 {num} 个
    - 采用杠铃型配置，兼顾风险和收益
    - A股，美股和港股占比均衡

    请以表格的方式输出投资组合，要求如下：

    - 包括股票名称, 股票代码
    - 股票在投资组合内的占比
    - 输出股票入选投资组合的原因
    - 交易频率或者再平衡周期建议
    - 根据投资组合风险等级的低中高顺序输出
    - 输出未入选投资组合的股票以及未入选原因。

    如果上述要求超出你能力范围，请列出超出你能力范围的要求。如果没有则不用列出。
    如果上述内容有表述不清楚的地方，请列出需要进一步精确表述的内容。如果没有则不用列出。
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

    for model in chat_models.keys():
        response = chat_models[model].invoke(messages)

        output_md = f"""# A股ETF投资组合 - {model}

        更新时间: {datetime.now().replace(microsecond=0)}

        模型: {chat_models[model].model_name}

        ## 投资组合参考

        {response.content}

        ## LLM 提示词

        {prompt}

        ## 免责声明

        {DISCLIAMER}
        """

        output_md = remove_leading_spaces(output_md)

        file_path = f"docs/portfolio/portfolio_cn_etf_{num}_{model}.md"

        with open(file_path, 'w') as f:
            f.write(output_md)
