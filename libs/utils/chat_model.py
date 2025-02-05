import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_openai.chat_models import ChatOpenAI

load_dotenv()

chat_models = {
    "zhipuai": ChatZhipuAI(
        model=os.environ.get("MODEL", "glm-4-flash"),
        temperature=0.01
    ),
    "deepseek": ChatOpenAI(
        model=os.environ.get("MODEL"),
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        temperature=0.00,
        base_url="https://api.deepseek.com"
    ),
    "moonshot": ChatOpenAI(
        model=os.environ.get("MODEL"),
        api_key=os.environ.get("MOONSHOT_API_KEY"),
        temperature=0.01,
        base_url="https://api.moonshot.cn/v1"
    )
}
