# 更新镜像并安装必要软件包
FROM ubuntu

RUN apt update && apt upgrade -y

RUN apt update && apt install -y build-essential curl python3-pip software-properties-common git

RUN pip install --no-cache-dir --break-system-packages \
    -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple \
    --ignore-installed cryptography \
    akshare colorama streamlit streamlit_authenticator

# # 将当前目录下的文件复制到容器的 /app 目录
COPY . /app

# # 覆盖生产环境配置
COPY .streamlit/config.prod.toml /app/.streamlit/config.toml

# # 设置工作目录
WORKDIR /app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/healthz

ENTRYPOINT ["streamlit", "run", "app.py"]