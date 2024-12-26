import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.document_loaders import DataFrameLoader
from langchain_core.messages import HumanMessage, SystemMessage
import pandas as pd

disclaimer = '本站用于实验目的，不构成任何投资建议，也不作为任何法律法规、监管政策的依据，\
    投资者不应以该等信息作为决策依据或依赖该等信息做出法律行为，由此造成的一切后果由投资者自行承担。'

load_dotenv()

chat = ChatZhipuAI(
    model="glm-4-plus",
    temperature=0.01,
)

df = pd.read_csv("selected.csv", dtype={'代码': str})

etf_cn = df[df["类型"] == "A股ETF"]

loader = DataFrameLoader(etf_cn, page_content_column="名称")

docs = loader.load()

num = 10

prompt = f"""

{docs}

以上是我选择的股票。请帮我构建一份投资组合，要求如下：

- 投资组合的股票数量为 {num} 个
- 美股占 40%，港股和A股各占 30%
- 采用杠铃型配置，兼顾风险和收益

请以表格的方式输出投资组合，要求如下：

- 包括股票名称和代码
- 股票在投资组合内的占比
- 输出股票入选投资组合的原因
- 以周为单位的交易频率建议
- 根据投资组合风险等级的低中高顺序输出

最后输出未入选投资组合的股票以及未入选原因。

"""

print(prompt)

messages = [
    SystemMessage(
        content="你是一个专业的投资人，可以根据我所给出的投资标的编制出投资组合"
    ),
    HumanMessage(
        content=prompt
    )
]

response = chat.invoke(messages)

output_md = f"""# 投资组合 - A股{num}ETF

## 投资组合参考

{response.content}

## LLM 提示词

{prompt}

## 免责声明

{disclaimer}

"""

file_path = f"docs/portfolio/portfolio_cn_etf_{num}.md"


with open(file_path, 'w') as f:
    f.write(output_md)
