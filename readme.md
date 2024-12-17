# Binance 新币公告监控工具

## 项目简介

这是一个用于监控币安(Binance)公告的自动化工具。它可以实时监控币安官方公告页面，当发现新的公告时，会通过企业微信机器人发送通知。

本项目主要用于:
- 实时获取币安公告信息
    - 新币上线
    - 新活动
    - 新公告
- 自动解析公告内容
- 通过企业微信机器人推送通知
- 支持Docker容器化部署

## 功能特点

### 核心功能
- 🔄 实时监控币安公告
- 📢 支持企业微信机器人通知
- 🔍 智能去重，避免重复通知

### 部署特性
- 🐳 支持 Docker 部署
- 🌐 支持代理设置
- 🕒 可配置监控间隔时间

### 其他特性
- 📝 详细的日志记录
- 🔄 自动重试机制
- ⚡ 异步处理架构

## 环境要求

- Python 3.9+
- Docker(可选,用于容器化部署)
- 企业微信机器人配置
- 网络代理(国内环境建议使用)

## 安装部署

### 方式一：直接运行

1. 克隆仓库：
```bash
git clone https://github.com/fanyilun0/binance-news-monitor
cd binance-news-monitor
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置参数：
编辑 `config.py` 文件，设置以下参数：
- `WEBHOOK_URL`：企业微信机器人的 webhook 地址
- `USE_PROXY`：是否使用代理
- `PROXY_URL`：代理服务器地址
- `MONITOR_INTERVAL`：监控间隔时间（秒）
- `COOKIE`：网页打开cookie (可选) 如果返回202，则需要配置cookie

4. 运行程序：
```bash
python main.py
```

### 方式二：Docker 部署

1. 构建并启动容器：
```bash
docker-compose up -d
```

## 配置说明

主要配置文件为 `config.py`，包含以下关键配置：

```python
# 根据环境变量判断是否在Docker中运行
IS_DOCKER = os.getenv('IS_DOCKER', 'false').lower() == 'true'

WEBHOOK_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='
# 根据运行环境选择代理地址
PROXY_URL = 'http://host.docker.internal:7890' if IS_DOCKER else 'http://localhost:7890'
USE_PROXY = True
ALWAYS_NOTIFY = False

# HTML URL
API_URL = "https://www.binance.com/en/support/announcement/new-cryptocurrency-listing?c=48&navId=48&hl=en"

# 监控周期，单位：秒
MONITOR_INTERVAL = 60  # 每隔 60 秒查询一次
```

## 通知示例

当检测到新币上线公告时，会发送如下格式的通知：

```
🚀 新币种上线公告 📢
标题: Binance Will List XXX (XXX)
时间: 2024-XX-XX XX:XX:XX
链接: https://www.binance.com/...
```

## 注意事项

1. 使用企业微信机器人需要配置正确的 webhook 地址
2. 如果在国内使用，建议配置代理
3. Docker 部署时需要确保主机的代理服务可以被容器访问

## 错误处理

程序会自动处理和记录以下情况：
- 网络连接错误
- API 响应超时
- 解析错误
- 代理连接问题

所有错误都会记录在日志中，并在控制台输出。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

MIT License