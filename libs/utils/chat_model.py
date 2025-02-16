import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_openai.chat_models import ChatOpenAI

load_dotenv()

chat_models = {
    "ollama": ChatOpenAI(
        model="deepseek-r1",
        api_key="ollama",
        temperature=0.01,
        base_url="http://localhost:11434/v1/"
    ),
    "zhipuai": ChatZhipuAI(
        model="glm-4-plus",
        temperature=0.01
    ),
    "deepseek": ChatOpenAI(
        model="deepseek-reasoner",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        temperature=0.00,
        base_url="https://api.deepseek.com"
    ),
    "moonshot": ChatOpenAI(
        model="moonshot-v1-32k",
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        temperature=0.01,
        base_url="https://api.moonshot.cn/v1"
    )
}
