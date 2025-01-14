from langchain_community.document_loaders import DataFrameLoader
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd

from libs.utils.chat_model import chat_models

disclaimer = '本站用于实验目的，不构成任何投资建议，也不作为任何法律法规、监管政策的依据，\
    投资者不应以该等信息作为决策依据或依赖该等信息做出法律行为，由此造成的一切后果由投资者自行承担。'


def create_portfolio():
    df = pd.read_csv("input/selected.csv", dtype={'代码': str})

    etf_cn = df[df["类型"] == "A股ETF"]

    loader = DataFrameLoader(etf_cn, page_content_column="名称")

    docs = loader.load()

    num = 10

    prompt = f"""{docs}是我选择的股票。

    请介绍每一只股票，并且帮我构建一份投资组合，要求如下：

    - 投资组合的股票数量为 {num} 个
    - 采用杠铃型配置，兼顾风险和收益
    - A股，美股和港股均衡配置

    请以表格的方式输出投资组合，要求如下：

    - 包括股票名称和代码
    - 股票在投资组合内的占比
    - 输出股票入选投资组合的原因
    - 交易频率或者再平衡周期建议
    - 根据投资组合风险等级的低中高顺序输出

    最后输出未入选投资组合的股票以及未入选原因。"""

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

        output_md = f"""# A股{num}ETF投资组合 - {model}

        模型: {chat_models[model].model_name}

        ## 投资组合参考

        {response.content}

        ## LLM 提示词

        {prompt}

        ## 免责声明

        {disclaimer}
        """.replace(" "*8, "")

        file_path = f"docs/portfolio/portfolio_cn_etf_{num}_{model}.md"

        with open(file_path, 'w') as f:
            f.write(output_md)