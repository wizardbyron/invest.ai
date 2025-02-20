import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_openai.chat_models import ChatOpenAI

load_dotenv()


def create_chat(service: str, model: str):
    temperature = float(os.environ.get("TEMPERATURE", 0.00))  # 默认值为 0.01
    chat_model_params = {
        "ollama": {
            "api_key": os.environ.get("OLLAMA_API_KEY"),
            "base_url": "http://localhost:11434/v1/"
        },
        "deepseek": {
            "api_key": os.environ.get("DEEPSEEK_API_KEY"),
            "base_url": "https://api.deepseek.com"
        },
        "moonshot": {
            "api_key": os.environ.get("MOONSHOT_API_KEY"),
            "base_url": "https://api.moonshot.cn/v1"
        }
    }

    if service == "zhipuai":
        return ChatZhipuAI(model=model, temperature=temperature)
    elif service in chat_model_params:
        params = chat_model_params[service]
        return ChatOpenAI(model=model, temperature=temperature, **params)
    else:
        raise ValueError(f"Unsupported service: {service}. ")
