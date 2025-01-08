import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 根据环境变量判断是否在Docker中运行
IS_DOCKER = os.getenv('IS_DOCKER', 'false').lower() == 'true'

# 获取API_KEY
WEBHOOK_KEY = os.getenv('WEBHOOK_KEY')

WEBHOOK_URL = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WEBHOOK_KEY}'   

# 根据运行环境选择代理地址
PROXY_URL = 'http://host.docker.internal:7890' if IS_DOCKER else 'http://localhost:7890'
USE_PROXY = True
ALWAYS_NOTIFY = True

# HTML URL
LISTING_API_URL = "https://www.binance.com/en/support/announcement/new-cryptocurrency-listing?c=48&navId=48&hl=en"
# 监控周期，单位：秒
MONITOR_INTERVAL = 60  # 每隔 60 秒查询一次

ENABLE_COINGLASS=True
# 指标图表URL
COINGLASS_URL = "https://www.coinglass.com/bull-market-peak-signals"

# 指标图表文件间隔
COINGLASS_FILE_INTERVAL = 24 * 60 * 60  # 24小时

