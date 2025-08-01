#!/usr/bin/env python
import time

import fire
import pandas as pd

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import WebBaseLoader

from src.llm import create_chat
from src.util import remove_leading_spaces, append_discliamer, nowstr


class PortfolioBuilder:

    def __init__(self):
        self.llm = [
            ("deepseek", "deepseek-reasoner"),
            ("ollama", "qwen3"),
            ("moonshot", "moonshot-v1-128k"),
            ("zhipuai", "glm-4.5")
        ]

    def selected(self, type: str = 'A股ETF', max: int = 10) -> str:
        """从已选清单生成投资组合

        Args:
            type (str, optional): _description_. Defaults to 'A股ETF'.
            max (int, optional): _description_. Defaults to 10.

        Returns:
            str: _description_
        """

        df = pd.read_csv("input/selected.csv", dtype={'代码': str})

        selected = df[df["类型"] == type]

        prompt = f"""以下是一份用于构建投资组合的{type}清单：

        {selected.to_markdown(index=False)}

        从上述清单中帮我构建一份投资组合，要求如下：

        - 投资组合的 {type} 的个数不超过 {max} 个
        - 采用杠铃型配置，兼顾风险和收益
        - 包含中国A股、中国香港、美国的投资标的，且在投资组合里的占比合理

        请以表格的方式输出投资组合，要求如下：

        - {type}名称及其代码, 以及在投资组合内的占比
        - 入选投资组合的原因
        - 投资组合的交易频率或者再平衡周期建议
        - 根据风险等级的低中高顺序输出

        并用以下格式输出投资组合中每个{type}的交易策略：

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

        for llm_service, model in self.llm:
            chat = create_chat(llm_service, model)

            try:
                print(f"模型: {model}")

                response = chat.invoke(messages)

                output_md = f"""# {type}投资组合(自选) - {llm_service}

                更新时间: {nowstr()}

                模型: {model}

                ## 投资组合参考

                {response.content}
                """
                output_md = append_discliamer(output_md)
                output_md = remove_leading_spaces(output_md)

                file_path = f"docs/投资组合/{type}全天候投资组合_{llm_service}.md"

                with open(file_path, "w") as f:
                    f.write(output_md)

            except Exception as e:
                print(f"调用模型[{model}]失败:\n{e}")

    def zero(self, type: str = 'A股ETF', max: int = 10) -> str:
        """从零生成投资组合

        Args:
            type (str, optional): 投资组合品种. Defaults to 'A股ETF'.
            max (int, optional): 投资组合品种数量. Defaults to 10.

        Returns:
            str: 投资组合文本
        """

        prompt = f"""请帮我构建一份{type}投资组合，要求如下：

        - 投资组合的 {type} 的个数不超过 {max} 个
        - 兼顾风险和收益
        - 包含中国A股、中国香港、美国的投资标的，且在投资组合里的占比合理

        请以表格的方式输出投资组合，要求如下：

        - {type}名称及其代码, 以及在投资组合内的占比
        - 入选投资组合的原因
        - 投资组合的交易频率或者再平衡周期建议
        - 根据风险等级的低中高顺序输出

        并用以下格式输出投资组合中每个{type}的交易策略：

        ## 风险等级

        ### {type} 的名称（{type}的交易代码）

        - 在投资组合内的占比
        - 入选投资组合的原因
        - 具体的交易策略，并解释交易策略
        - 交易频率
        - 每个 {type} 的止盈和止损策略

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

        for llm_service, model in self.llm:
            chat = create_chat(llm_service, model)

            try:
                print(f"模型: {model}")

                response = chat.invoke(messages)

                output_md = f"""# {type}投资组合 - {llm_service}

                更新时间: {nowstr()}

                模型: {model}

                ## 投资组合参考

                {response.content}
                """
                output_md = append_discliamer(output_md)
                output_md = remove_leading_spaces(output_md)

                file_path = f"docs/投资组合/{type}投资组合_{llm_service}.md"

                with open(file_path, "w") as f:
                    f.write(output_md)

            except Exception as e:
                print(f"调用模型[{model}]失败:\n{e}")

    def __evaluate(self, portfolio_text: str) -> str:
        prompt = f"""以下是一份投资组合说明：

        {portfolio_text}

        请评价这个投资组合的优点和不足，并给出进一步优化建议。
        """

        prompt = remove_leading_spaces(prompt)

        # print(prompt)

        messages = [
            SystemMessage(
                content="你是一个专业的投资人，可以根据我所给出的投资组合给出评价，并给出调整方案。"
            ),
            HumanMessage(
                content=prompt
            )
        ]

        chat = create_chat("deepseek", "deepseek-reasoner")

        response = chat.invoke(messages)

        return response.content

    def evaluate(self, url: str):
        """对投资组合进行评估

        Args:
            url (str): 评估URL提供的的投资组合
        """
        loader = WebBaseLoader(url)
        doc = loader.load()
        page = doc[0].page_content
        page = page[page.find("更新时间"):]

        print(self.__evaluate(doc[0].page_content))

    def all_whethers(self, type: str = "A股ETF"):
        """全天候投资组合

        Args:
            type (str, optional): 品种名称. Defaults to "A股ETF".
        """

        prompt = f"""请帮我构建一份{type}的全天候投资组合，要求如下：

        - 请以表格的方式输出投资组合
        - {type}的代码名称, 以及在投资组合内的占比
        - 入选投资组合的原因
        - 投资组合的交易频率或者再平衡周期建议
        - 根据风险等级的低中高顺序输出

        并用以下格式输出投资组合的交易策略：

        ## 风险等级

        ### {type} 的名称（{type}的交易代码）

        - 在投资组合内的占比
        - 入选投资组合的原因
        - 具体的交易策略，并解释交易策略
        - 交易频率
        - 每个 {type} 的止盈和止损策略

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

        for llm_service, model in self.llm:
            chat = create_chat(llm_service, model)

            try:
                print(f"模型: {model}")

                response = chat.invoke(messages)

                output_md = f"""# {type}全天候投资组合 - {llm_service}

                更新时间: {nowstr()}

                模型: {model}

                ## 投资组合参考

                {response.content}
                """
                output_md = append_discliamer(output_md)
                output_md = remove_leading_spaces(output_md)

                file_path = f"docs/投资组合/{type}全天候投资组合_{llm_service}.md"

                with open(file_path, "w") as f:
                    f.write(output_md)

            except Exception as e:
                print(f"调用模型[{model}]失败:\n{e}")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(PortfolioBuilder)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
