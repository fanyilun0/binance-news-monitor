# Binance 新币公告监控工具

## 项目简介

这是一个用于监控币安(Binance)公告和市场指标的自动化工具。它可以实时监控币安官方公告页面和 Coinglass 市场指标，并通过企业微信机器人发送通知。

## 功能特点

### 核心功能
- 🔄 实时监控币安公告
  - 新币上线通知
  - 新活动通知
  - 重要公告推送
- 📊 Coinglass 市场指标监控
  - 牛市顶部信号监控
  - 定时图表推送
- 📢 企业微信机器人通知
  - 文本消息推送
  - 图片消息推送

### 技术特性
- 🔍 智能去重，避免重复通知
- 🔑 Cookie 自动更新机制
- 🕒 可配置监控间隔
- 📝 详细的日志记录
- 🔄 自动重试机制
- 🔀  异步处理架构

### 部署特性
- 🐳 支持 Docker 部署
- 🌐 支持代理设置
- 🛠️ 简单的环境变量配置

## 环境要求

- Python 3.9+
- Playwright
- Docker (可选，用于容器化部署)
- 企业微信机器人
- 网络代理 (国内环境建议使用)

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
python -m playwright install chromium
```

3. 配置参数：
创建 `.env` 文件，配置以下参数：
```bash
# 企业微信机器人配置
WEBHOOK_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

4. 运行程序：
```bash
python main.py  # 运行所有监控
```
或分别运行：
```bash
python binanceListing.py  # 运行币安监控
python coinglass.py  # 单独运行Coinglass监控
```

### 方式二：Docker 部署

1. 配置同上，创建 `.env` 文件并设置参数
2. 构建并启动容器：
```bash
docker-compose up -d
```

## 功能说明

### Binance新币上线监控
- 实时监控币安新币上线公告
- 智能解析公告内容
- 通过企业微信推送通知
- 自动过滤重复公告

### Coinglass指标监控
- 监控Coinglass牛市顶部信号
- 定时抓取指标图表
- 通过企业微信推送图片
- 可配置监控间隔

## 配置说明

### 必要配置 (.env)
```bash
# 企业微信机器人配置
WEBHOOK_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 可选配置 (config.py)
其他参数已内置默认配置，一般情况下无需修改。如需自定义，可以修改 `config.py`：
- `MONITOR_INTERVAL`: 币安监控间隔（默认60秒）
- `COINGLASS_FILE_INTERVAL`: Coinglass图表更新间隔（默认24小时）
- `USE_PROXY`: 是否使用代理
- `PROXY_URL`: 代理服务器地址

## 通知示例
当检测到新公告时，会发送如下格式的通知：

```
🚀 新币种上线公告
📌: Binance Will List XXX (XXX)
🕒: 2024-XX-XX XX:XX:XX
🔗: https://www.binance.com/...
```

## 注意事项

1. 首次运行时需要安装依赖并配置环境变量
2. 国内环境建议配置代理
3. Docker部署时注意配置正确的环境变量
4. 建议定期检查日志确保程序正常运行

## 常见问题

1. 如何获取企业微信机器人的Webhook Key？
   - 在企业微信群组中添加机器人
   - 获取机器人的Webhook URL
   - 提取URL中的key部分

2. 程序报错无法连接？
   - 检查网络连接
   - 确认代理配置是否正确
   - 验证环境变量是否正确设置

3. Docker部署失败？
   - 确认Docker环境正确安装
   - 检查.env文件配置
   - 查看容器日志排查问题

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

MIT License
