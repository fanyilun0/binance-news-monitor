# 使用playwright官方镜像
FROM mcr.microsoft.com/playwright:v1.41.0-jammy

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# 设置构建时的代理环境变量
ARG HTTP_PROXY
ARG HTTPS_PROXY

WORKDIR /app

# 安装 pip
#RUN apt-get update && apt-get install -y python3-pip
# 使用阿里云镜像源安装 pip
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y python3-pip

# 配置pip镜像源
# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
#     && pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn \
#     && pip config set global.timeout 120
# 配置pip使用阿里云镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip config set global.trusted-host mirrors.aliyun.com \
    && pip config set global.timeout 120

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || (echo "Failed to install requirements" && exit 1)

# 安装playwright
RUN python3 -m playwright install chromium || (echo "Failed to install playwright browsers" && exit 1)

# 验证安装
RUN python3 -c "from playwright.async_api import async_playwright" || (echo "Failed to import playwright" && exit 1)

# 复制程序文件
COPY . .

# 设置运行时的代理环境变量
ENV HTTP_PROXY=${HTTP_PROXY:-""}
ENV HTTPS_PROXY=${HTTPS_PROXY:-""}

# 运行程序
CMD ["python3", "-u", "main.py"] 
