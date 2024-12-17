import requests
import aiohttp
import random
from datetime import datetime
from typing import Optional, Dict, Any, List
import os
from pathlib import Path
import json

from config import WEBHOOK_URL, PROXY_URL, USE_PROXY, COOKIE

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

# Emoji映射字典
EMOJI_MAPPINGS = {
    # 上币公告
    'listing': {
        "Introducing": "🚀",
        "上线": "🚀",
        "Launchpool": "🌱", 
        "Futures": "📈",
        "Options": "📊",
        "Margin": "💹"
    },
    # 新闻公告
    'news': {
        "Binance": "📢",
        "币安": "📢",
        "Announcement": "📣",
        "公告": "📣",
        "Notice": "ℹ️",
        "通知": "ℹ️"
    },
    # 活动公告
    'activities': {
        "Rewards": "🎁",
        "奖励": "🎁",
        "Campaign": "🎯",
        "活动": "🎯",
        "Airdrop": "🪂",
        "空投": "🪂",
        "Staking": "🏆",
        "质押": "🏆"
    }
}

# 文件路径相关配置
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# 文件名配置
LISTING_RAW_FILE = "listing_raw.html"
LISTING_PARSED_FILE = "listing_parsed.json"

def get_emoji_for_type(title: str, announcement_type: str) -> str:
    """根据公告标题和类型返回相应的emoji
    
    Args:
        title: 公告标题
        announcement_type: 公告类型('listing', 'news', 'activities')
        
    Returns:
        对应的emoji字符串
    """
    emoji_map = EMOJI_MAPPINGS.get(announcement_type, {})
    return next((emoji for keyword, emoji in emoji_map.items() 
                if keyword in title), "ℹ️")

def build_article_link(article_id: str, category: str = '') -> str:
    """构建文章链接
    
    Args:
        article_id: 文章ID
        category: 分类('listing', 'news', 'activities')
        
    Returns:
        完整的文章URL
    """
    base_url = "https://www.binance.com/en/support/announcement/"
    
    # 根据不同类型添加不同的参数
    category_params = {
        'listing': '?c=48&navId=48',
        'news': '?c=49&navId=49',
        'activities': '?c=50&navId=50'
    }
    
    params = category_params.get(category, '')
    return f"{base_url}{article_id}{params}"

def build_message(title: str, 
                 release_date: str, 
                 link: str,
                 announcement_type: str,
                 is_initial: bool = False) -> str:
    """构建通用的推送消息
    
    Args:
        title: 公告标题
        release_date: 发布时间
        link: 文章链接
        announcement_type: 公告类型('listing', 'news', 'activities')
        is_initial: 是否为初始化消息
        
    Returns:
        格式化的消息字符串
    """
    emoji = get_emoji_for_type(title, announcement_type)
    
    # 根据不同类型设置不同的前缀
    prefix_map = {
        'listing': "新币种上线公告",
        'news': "币安新闻公告",
        'activities': "币安活动公告"
    }
    
    if is_initial:
        prefix = f"📢 Initial {prefix_map.get(announcement_type, '')} Alert 📢"
    else:
        prefix = f"{emoji} {prefix_map.get(announcement_type, '')} 📢"
    
    return (
        f"{prefix}\n"
        f"标题: {title}\n"
        f"时间: {release_date}\n"
        f"链接: {link if link else '无链接'}"
    )

async def send_message_async(message_content: str) -> None:
    """发送消息到企业微信机器人"""
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }
    
    proxy = PROXY_URL if USE_PROXY else None
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL, json=payload, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                log_with_time("Message sent successfully!")
            else:
                log_with_time(f"Failed to send message: {response.status}")

def log_with_time(message: str, module: str = '') -> None:
    """打印带时间戳和模块名的消息
    
    Args:
        message: 日志消息
        module: 模块名称
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    module_prefix = f"[{module}] " if module else ""
    print(f"[{current_time}] {module_prefix}{message}")

def get_random_headers(referer: str = '') -> Dict[str, str]:
    """生成随机请求头"""
    return {
        'authority': 'www.binance.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'cache-control': 'max-age=0',
        'User-Agent': random.choice(USER_AGENTS),
        'cookie': COOKIE,
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'
    }

async def initialize_monitor(save_and_parse_func: callable, 
                           send_notifications_func: callable,
                           always_notify: bool = False) -> tuple:
    """通用的监控初始化函数"""
    initial_articles = save_and_parse_func()
    if initial_articles:
        article_ids = {article['id'] for article in initial_articles}
        log_with_time(f"Initialized with {len(article_ids)} articles")
        
        if always_notify:
            await send_notifications_func(initial_articles, is_initial=True)
            
        return article_ids, initial_articles
    return set(), []

async def check_new_articles(save_and_parse_func: callable, 
                           last_ids: set) -> tuple:
    """通用的检查新文章函数"""
    articles = await save_and_parse_func()
    if not articles:
        return None, set()
        
    current_ids = {article['id'] for article in articles}
    new_ids = current_ids - last_ids
    
    return articles, new_ids

async def fetch_and_save_html_content(url: str, filename: str) -> Optional[str]:
    """获取指定URL的HTML内容并保存
    Args:
        url: 要请求的URL
        filename: 保存HTML内容的文件名
    Returns:
        响应的文本内容，如果请求失败则返回None
    """
    try:
        headers = get_random_headers(url)
        response = requests.get(url, headers=headers)
        log_with_time(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            log_with_time(f"Failed to fetch data: {response.status_code}")
            return None

        save_html_content(response.text, filename)
        return response.text
        
    except Exception as e:
        log_with_time(f"Error fetching data from {url}: {e}")
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