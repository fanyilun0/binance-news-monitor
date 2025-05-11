import aiohttp
import random
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import asyncio
import re
import time
import subprocess
import shlex
import base64
from urllib.parse import urlparse, parse_qs

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
    formatted_title = re.sub(r'[()!?.,:""#&]', '', formatted_title)
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

def get_random_user_agent() -> str:
    """随机选择一个用户代理"""
    return random.choice(USER_AGENTS)

async def get_headers(referer: str = '') -> Dict[str, str]:
    """生成高度模拟真实浏览器的请求头"""
    cookie = cookie_manager.get_cookies()
    if not cookie:
        try:
            cookie = await cookie_manager.update_cookies()
        except Exception as e:
            log_with_time(f"Failed to get cookies: {e}")
            raise
    
    # 随机选择用户代理
    user_agent = get_random_user_agent()
    
    # 生成随机的浏览器特征
    chrome_version = random.randint(100, 135)
    platform = random.choice(["macOS", "Windows"])
    
    # 添加更多真实的浏览器指纹
    headers = {
        'authority': 'www.binance.com',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'cookie': cookie,
        'sec-ch-ua': f'"Google Chrome";v="{chrome_version}", "Not-A.Brand";v="8", "Chromium";v="{chrome_version}"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': f'"{platform}"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
        # 添加随机浏览器指纹参数
        'viewport-width': f'{random.choice([1280, 1440, 1920])}',
        'device-memory': f'{random.choice([4, 8, 16])}',
        'dpr': f'{random.choice([1, 2])}',
        'priority': 'u=0, i'
    }
    
    # 如果提供了referer，添加到头部
    if referer:
        headers['referer'] = referer
    else:
        # 使用随机的前导页面作为referer
        referers = [
            'https://www.binance.com/en',
            'https://www.binance.com/en/markets',
            'https://www.binance.com/en/trade',
            'https://www.binance.com/en/my/dashboard'
        ]
        headers['referer'] = random.choice(referers)
        
    return headers

async def fetch_with_curl(url: str, cookie: str, proxy: str = None) -> Optional[str]:
    """使用curl命令获取网页内容"""
    try:
        cmd = [
            'curl', 
            url,
            '-H', f'Cookie: {cookie}',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            '-H', 'Cache-Control: max-age=0',
            '-H', 'sec-ch-ua: "Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            '-H', 'sec-ch-ua-mobile: ?0',
            '-H', 'sec-ch-ua-platform: "macOS"',
            '-H', 'sec-fetch-dest: document',
            '-H', 'sec-fetch-mode: navigate',
            '-H', 'sec-fetch-site: same-origin',
            '-H', 'sec-fetch-user: ?1',
            '-H', 'upgrade-insecure-requests: 1',
            '--compressed',
            '-s',  # 静默模式
            '-L'   # 跟随重定向
        ]
        
        # 如果有代理，添加代理设置
        if proxy:
            cmd.extend(['--proxy', proxy])
            
        log_with_time(f"Executing curl command for {url}")
        
        # 使用异步子进程运行curl
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            log_with_time(f"Curl command failed: {stderr.decode()}")
            return None
            
        return stdout.decode('utf-8')
    except Exception as e:
        log_with_time(f"Error executing curl: {e}")
        return None

async def handle_human_verification(content: str) -> bool:
    """处理人机验证页面，提醒用户需要手动验证"""
    # 检查是否包含人机验证的特征
    if "Human Verification" in content or "captcha" in content or "AwsWafIntegration" in content:
        log_with_time("⚠️ 检测到人机验证页面！")
        
        # 从HTML内容中提取AWS WAF相关信息
        aws_token_match = re.search(r'aws-waf-token=([^;"]+)', content)
        aws_token = aws_token_match.group(1) if aws_token_match else None
        
        # 尝试自动更新cookie
        try:
            new_cookie = await cookie_manager.update_cookies()
            if new_cookie and new_cookie != cookie_manager.get_cookies():
                log_with_time("✅ 成功自动更新Cookie")
                return False  # 不发送通知，直接重试
        except Exception as e:
            log_with_time(f"❌ 自动更新Cookie失败: {e}")
        
        # 如果自动更新失败，发送通知给用户
        message = (
            "⚠️ 人机验证拦截\n"
            "币安网站已启用人机验证，需要您手动操作：\n"
            "1. 请访问币安公告页面并完成验证\n"
            "2. 完成验证后复制新cookie并更新配置\n"
            f"AWS Token: {aws_token if aws_token else '未找到'}"
        )
        await send_message_async(message, is_error=True)
        return True
    
    return False

async def fetch_and_save_html_content(url: str, filename: str, max_retries: int = 3) -> Optional[str]:
    """获取并保存HTML内容,支持cookie自动更新"""
    for attempt in range(max_retries):
        try:
            # 使用固定的时间戳参数
            if '?' in url:
                base_url, params = url.split('?', 1)
                params_dict = {}
                for param in params.split('&'):
                    if '=' in param:
                        k, v = param.split('=', 1)
                        params_dict[k] = v
                
                # 确保有navId参数
                if 'navId' not in params_dict:
                    params_dict['navId'] = '48'
                    
                # 使用固定时间戳
                params_dict['t'] = str(int(time.time()))
                
                # 重建URL
                query_params = '&'.join([f"{k}={v}" for k, v in params_dict.items()])
                url_with_params = f"{base_url}?{query_params}"
            else:
                # 如果URL没有参数，添加必要的参数
                url_with_params = f"{url}?navId=48&t={int(time.time())}"
            
            log_with_time(f"Starting request to {url_with_params}")
            
            # 获取cookie
            cookie = cookie_manager.get_cookies()
            if not cookie:
                cookie = await cookie_manager.update_cookies()
                
            log_with_time(f"Using cookie: {cookie[:50]}...")
            
            proxy = PROXY_URL if USE_PROXY else None
            log_with_time(f"Attempt {attempt + 1}/{max_retries} with proxy: {proxy}")
            
            # 首先尝试使用curl，它通常比aiohttp更好地模拟浏览器
            curl_content = await fetch_with_curl(url_with_params, cookie, proxy)
            if curl_content:
                log_with_time("🔄 Successfully fetched content with curl")
                
                # 检查是否是人机验证页面
                if await handle_human_verification(curl_content):
                    # 如果是人机验证页面，保存到文件以便分析
                    file_path = DATA_DIR / f"captcha_{filename}"
                    file_path.write_text(curl_content, encoding='utf-8')
                    log_with_time(f"💾 Captcha page saved to {file_path}")
                    return None
                
                # 保存内容到文件
                file_path = DATA_DIR / filename
                file_path.write_text(curl_content, encoding='utf-8')
                log_with_time(f"💾 Content saved to {file_path}")
                return curl_content
            else:
                log_with_time("❌ Failed to fetch content with curl, trying aiohttp...")
            
            # 如果curl失败，尝试使用aiohttp
            try:
                headers = await get_headers()
                regular_headers = {k: v for k, v in headers.items() if not k.startswith(':')}
                
                # 添加随机的可接受格式和编码，以及更多的浏览器特征
                regular_headers['Accept-Encoding'] = 'gzip, deflate, br'
                regular_headers['Connection'] = 'keep-alive'
                
                # 添加referer头，模拟从币安主页访问
                regular_headers['Referer'] = 'https://www.binance.com/en'
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url_with_params, 
                        headers=regular_headers, 
                        proxy=proxy,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        log_with_time(f"🔄 Response status: {response.status}")
                        
                        if response.status == 200:
                            content = await response.text()
                            
                            # 检查是否是人机验证页面
                            if await handle_human_verification(content):
                                # 如果是人机验证页面，保存到文件以便分析
                                file_path = DATA_DIR / f"captcha_{filename}"
                                file_path.write_text(content, encoding='utf-8')
                                log_with_time(f"💾 Captcha page saved to {file_path}")
                                return None
                            
                            # 保存内容到文件
                            file_path = DATA_DIR / filename
                            file_path.write_text(content, encoding='utf-8')
                            log_with_time(f"💾 Content saved to {file_path}")
                            return content
                        elif response.status == 202:
                            log_with_time("🔑 Cookie expired, updating...")
                            await cookie_manager.update_cookies()
                            continue
                        else:
                            log_with_time(f"❌ Request failed with status: {response.status}")
            except aiohttp.ClientError as e:
                log_with_time(f"aiohttp request failed: {e}")
                    
        except Exception as e:
            log_with_time(f"Error in attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
            
        # 指数退避
        retry_delay = 2 ** attempt
        log_with_time(f"Retrying in {retry_delay} seconds...")
        await asyncio.sleep(retry_delay)
    
    # 所有尝试都失败后，发送通知
    await send_message_async("❌ 无法获取币安公告列表，请检查网络或更新Cookie", is_error=True)
    return None

async def update_cookie_from_file(file_path: str) -> bool:
    """从文件更新cookie"""
    try:
        path = Path(file_path)
        if not path.exists():
            log_with_time(f"Cookie文件不存在: {file_path}")
            return False
            
        cookie = path.read_text().strip()
        if not cookie:
            log_with_time("Cookie文件为空")
            return False
            
        # 更新cookie
        cookie_manager.update_cookie_from_str(cookie)
        log_with_time("成功从文件更新cookie")
        return True
    except Exception as e:
        log_with_time(f"从文件更新cookie失败: {e}")
        return False

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