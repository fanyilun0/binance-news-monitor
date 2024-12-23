import os

# 根据环境变量判断是否在Docker中运行
IS_DOCKER = os.getenv('IS_DOCKER', 'false').lower() == 'true'

WEBHOOK_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='   

# 根据运行环境选择代理地址
PROXY_URL = 'http://host.docker.internal:7890' if IS_DOCKER else 'http://localhost:7890'
USE_PROXY = True
ALWAYS_NOTIFY = True

# HTML URL
LISTING_API_URL = "https://www.binance.com/en/support/announcement/new-cryptocurrency-listing?c=48&navId=48&hl=en"
# 监控周期，单位：秒
MONITOR_INTERVAL = 60  # 每隔 60 秒查询一次

COOKIE_FILE = "cookies.txt"
