import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import DataFrameLoader
import pandas as pd

load_dotenv()

os.environ.get("ZHIPUAI_API_KEY")

chat = ChatZhipuAI(
    model="glm-4-plus",
    temperature=0.1,
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
- 保留或者剔除某个股票的原因
- 以周为单位的交易频率建议

"""

messages = [
    SystemMessage(
        content="你是一个专业的投资人，可以根据我所给出的投资标的编制出投资组合"
    ),
    HumanMessage(
        content=prompt
    )
]

response = chat.invoke(messages)

output_md = f"""# 投资组合

## 投资组合参考

{response.content}

## LLM 提示词

{prompt}

"""

file_path = f"docs/portfolio/portfolio_{num}.md"


with open(file_path, 'w') as f:
    f.write(output_md)
