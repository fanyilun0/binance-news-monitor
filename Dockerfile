# 使用playwright官方镜像
FROM mcr.microsoft.com/playwright:v1.41.0-jammy

# 设置环境变量，禁用Python的输出缓冲
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# 设置构建时的代理环境变量
ARG HTTP_PROXY
ARG HTTPS_PROXY

WORKDIR /app

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
RUN pip install -r requirements.txt

# 复制程序文件
COPY . .

# 设置运行时的代理环境变量
ENV HTTP_PROXY=${HTTP_PROXY:-""}
ENV HTTPS_PROXY=${HTTPS_PROXY:-""}

# 运行程序
CMD ["python", "-u", "main.py"] 
