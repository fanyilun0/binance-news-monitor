import aiohttp
import random
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import asyncio
import re

from cookie import CookieManager
from config import WEBHOOK_URL, PROXY_URL, USE_PROXY
from emoji import get_emoji_and_type

# User-Agent池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
]

# 文件路径相关配置
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# 文件名配置
LISTING_RAW_FILE = "listing_raw.html"
LISTING_PARSED_FILE = "listing_parsed.json"

# 添加错误推送限制相关的全局变量
ERROR_MSG_LIMIT = 5  # 每个时间窗口内的最大错误推送次数
ERROR_MSG_WINDOW = 3600  # 时间窗口大小(秒)
error_msg_count = 0
last_error_reset_time = datetime.now()

# 初始化CookieManager
cookie_manager = CookieManager()

def build_article_link(title: str, code: str) -> str:
    """构建文章链接
    
    Args:
        title: 文章标题
        code: 文章code(不是id)
        
    Returns:
        格式化后的文章链接
    """
    base_url = "https://www.binance.com/en/support/announcement/"
    
    # 处理标题格式
    formatted_title = title.lower()
    # 使用正则表达式移除特定标点符号，将撇号替换为连字符
    formatted_title = re.sub(r'[()!?.,:“”#&]', '', formatted_title)
    formatted_title = formatted_title.replace("'", "-")
    # 将连续的空格替换为单个破折号
    formatted_title = re.sub(r'\s+', '-', formatted_title)
    
    return f"{base_url}{formatted_title}-{code}"

def build_message(title: str, 
                 release_date: str, 
                 link: str
                 ) -> str:
    """构建通用的推送消息
    
    Args:
        title: 公告标题
        release_date: 发布时间
        link: 文章链接
        
    Returns:
        格式化的消息字符串
    """
    emoji, type = get_emoji_and_type(title)
    
    return (
        f"{emoji} {type}\n"
        f"📌: {title}\n"
        f"🕒: {release_date}\n"
        f"🔗: {link if link else '无链接'}"
    )

async def send_message_async(message_content: str, is_error: bool = False) -> None:
    """发送消息到企业微信机器人
    
    Args:
        message_content: 要发送的消息内容
        is_error: 是否为错误消息
    """
    global error_msg_count, last_error_reset_time
    
    # 检查是否需要重置错误计数
    now = datetime.now()
    if (now - last_error_reset_time).total_seconds() >= ERROR_MSG_WINDOW:
        error_msg_count = 0
        last_error_reset_time = now
    
    # 如果是错误消息且已达到限制,则只记录日志
    if is_error:
        if error_msg_count >= ERROR_MSG_LIMIT:
            log_with_time(f"Error message suppressed (limit reached): {message_content}")
            return
        error_msg_count += 1
        
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }
    
    log_with_time(f"Sending message: {message_content}")

    proxy = PROXY_URL if USE_PROXY else None
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL, json=payload, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                log_with_time("Message sent successfully!")
            else:
                log_with_time(f"Failed to send message: {response.status}")

def log_with_time(message: str, module: str = '') -> None:
    """打印带时间戳和模块名的消息"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

async def get_headers(referer: str = '') -> Dict[str, str]:
    """生成请求头,支持自动更新cookie"""
    cookie = cookie_manager.get_cookies()
    if not cookie:
        try:
            cookie = await cookie_manager.update_cookies()
        except Exception as e:
            log_with_time(f"Failed to get cookies: {e}")
            raise
    
    return {
        'authority': 'www.binance.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'cache-control': 'max-age=0',
        'User-Agent': random.choice(USER_AGENTS),
        'cookie': cookie,
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'
    }

async def fetch_and_save_html_content(url: str, filename: str, max_retries: int = 3) -> Optional[str]:
    """获取并保存HTML内容,支持cookie自动更新"""
    for attempt in range(max_retries):
        try:
            headers = await get_headers()
            log_with_time(f"Starting request to {url}")
            log_with_time(f"Using cookie: {headers['cookie'][:50]}...")
            
            proxy = PROXY_URL if USE_PROXY else None
            log_with_time(f"Attempt {attempt + 1}/{max_retries} with proxy: {proxy}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, proxy=proxy) as response:
                    log_with_time(f"🔄 Response status: {response.status}")
                    
                    if response.status == 202:
                        log_with_time("🔑 Cookie expired, updating...")
                        await cookie_manager.update_cookies()
                        continue
                        
                    if response.status == 200:
                        content = await response.text()
                        
                        # 保存内容到文件
                        file_path = DATA_DIR / filename
                        file_path.write_text(content, encoding='utf-8')
                        log_with_time(f"💾 Content saved to {file_path}")
                        
                        return content
                    else:
                        log_with_time(f"❌ Request failed with status: {response.status}")
                        
        except Exception as e:
            log_with_time(f"Error in attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
            
        await asyncio.sleep(2 ** attempt)  # 指数退避
    
    return None

def save_html_content(response_text: str, filename: str) -> None:
    """保存HTML内容到data目录下的文件
    
    Args:
        response_text: 要保存的HTML内容
        filename: 文件名
    """
    try:
        file_path = DATA_DIR / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response_text)
        log_with_time(f"Raw HTML saved to {file_path}")
    except Exception as e:
        log_with_time(f"Error saving HTML content: {e}")

def get_last_articles_from_file(filename: str = LISTING_PARSED_FILE) -> set:
    """从本地JSON文件中读取上次的文章ID集合
    
    Args:
        filename: JSON文件名，默认为"listing_parsed.json"
        
    Returns:
        文章ID集合
    """
    try:
        json_path = DATA_DIR / filename
        if not json_path.exists():
            log_with_time(f"No existing file found at {json_path}")
            return set()
            
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            
        # 查找包含 catalogDetail 的路由
        for route_content in json_data['appState']['loader']['dataByRouteId'].values():
            if 'catalogDetail' in route_content:
                articles = route_content['catalogDetail']['articles']
                log_with_time(f"Loaded {len(articles)} articles from {filename}")
                return {article['id'] for article in articles}
                
        log_with_time(f"No articles found in {filename}")
        return set()
    except Exception as e:
        log_with_time(f"Error reading last articles from file: {e}")
        return set()