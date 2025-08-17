# 使用 Python 基础镜像
FROM ubuntu
RUN apt update && apt install -y python3-pip && rm -rf /var/lib/apt/lists/*

# 将当前目录下的文件复制到容器的 /app 目录
COPY . /app

# 设置工作目录
WORKDIR /app

RUN pip install --no-cache-dir --break-system-packages -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple akshare streamlit

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--client.toolbarMode=minimal","--server.disconnectedSessionTTL=3600", "--browser.gatherUsageStats=False"]