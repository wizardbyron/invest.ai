#!/usr/bin/env python
import time

import fire
import pandas as pd

from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import create_chat
from src.util import remove_leading_spaces, append_discliamer, nowstr


class AllWeatherPortfolioBuilder:
    def __init__(self):
        pass

    def build_from_all(self, max_stocks: int = 10) -> None:
        """从all.csv构建全天候投资组合

        Args:
            max_stocks (int, optional): 投资组合证券数量. Defaults to 10.

        Returns:
            str: 投资组合文本
        """

        df = pd.read_csv("input/portfolios/all.csv", dtype={"代码": str})

        available_stocks = df.to_markdown(index=False)

        prompt = f"""以下是一份可用于构建投资组合的证券清单：

        {available_stocks}

        请帮我从上述清单中挑选{max_stocks}只证券，构建一份全天候投资组合，要求如下：

        - 投资组合的证券个数不超过 {max_stocks} 只
        - 基于Ray Dalio的全天候投资组合理念，在以下经济环境中都能获得稳定收益：
          - 经济增长高于预期
          - 经济增长低于预期
          - 通货膨胀高于预期
          - 通货膨胀低于预期
        - 投资组合应该包含不同资产类别
        - 从上述清单中选择最合适的证券
        - 采用风险平价理念，让各类资产贡献相同的风险
        - 兼顾中国A股、中国香港、美国的投资标的，且在投资组合里的占比合理
        - 考虑投资组合的再平衡周期

        请以表格的方式输出投资组合，要求如下：

        - 证券名称及其代码, 以及在投资组合内的占比
        - 入选投资组合的原因（结合全天候投资组合理论）
        - 投资组合的交易频率或者再平衡周期建议
        - 根据风险等级的低中高顺序输出

        并用以下格式输出投资组合中每个证券的交易策略：

        ## 风险等级

        ### 证券的名称（证券的交易代码）

        - 在投资组合内的占比
        - 入选投资组合的原因（结合全天候投资组合理论，说明该证券在哪种经济环境下表现较好）
        - 具体的交易策略，并解释交易策略
        - 交易频率
        - 止盈和止损策略

        ## 投资组合交易策略

        ## 经济环境适应性分析
        """

        prompt = remove_leading_spaces(prompt)

        print(prompt)

        messages = [
            SystemMessage(
                content="你是一个专业的投资人，精通Ray Dalio的全天候投资组合理论，可以根据已给出的投资标的编制出投资组合，做到在不同经济环境下风险和收益兼顾。"
            ),
            HumanMessage(content=prompt),
        ]

        llm_list = [  # ("deepseek", "deepseek-reasoner"),
            ("zai", "glm-4.5-flash")]
        # ("aliyun", "qwen-flash")]

        for llm_service, model in llm_list:
            chat = create_chat(llm_service, model)

            try:
                print(f"模型: {model}")

                response = chat.invoke(messages)

                output_md = f"""# 全天候投资组合（从all.csv挑选） - {llm_service}

                更新时间: {nowstr()}

                模型: {model}

                ## 投资组合参考

                {response.content}
                """
                output_md = append_discliamer(output_md)
                output_md = remove_leading_spaces(output_md)

                file_path = f"docs/投资组合/全天候投资组合_{llm_service}.md"

                with open(file_path, "w") as f:
                    f.write(output_md)

            except Exception as e:
                print(f"调用模型[{model}]失败:\n{e}")


if __name__ == "__main__":
    start_time = time.time()
    fire.Fire(AllWeatherPortfolioBuilder)
    end_time = time.time()
    duration = end_time - start_time
    print(f"[生成结果用时：{duration:.2f}秒]")
