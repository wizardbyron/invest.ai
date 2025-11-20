import os

from dotenv import load_dotenv

from langchain_openai.chat_models import ChatOpenAI


load_dotenv()


def create_chat(service: str, model: str):
    """
    创建大模型服务调用

    Args:
        service (str): 大模型服务
        model (str): 模型名称

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    chat_model_params = {
        "aliyun": {
            "api_key": os.environ.get("ALIYUN_API_KEY"),
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/"
        },
        "ollama": {
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1/"
        },
        "deepseek": {
            "api_key": os.environ.get("DEEPSEEK_API_KEY"),
            "base_url": "https://api.deepseek.com"
        },
        "moonshot": {
            "api_key": os.environ.get("MOONSHOT_API_KEY"),
            "base_url": "https://api.moonshot.cn/v1/"
        },
        "zai": {
            "api_key": os.environ.get("ZAI_API_KEY"),
            "base_url": "https://open.bigmodel.cn/api/paas/v4/"
        }
    }

    params = chat_model_params[service]

    return ChatOpenAI(model=model, temperature=0.01, **params)
