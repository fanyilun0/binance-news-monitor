import asyncio
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

from config import COOKIE, ALWAYS_NOTIFY, LISTING_API_URL, MONITOR_INTERVAL
from util import (
    DATA_DIR,
    LISTING_RAW_FILE,
    LISTING_PARSED_FILE,
    send_message_async,
    log_with_time,
    build_article_link,
    build_message,
    check_new_articles,
    fetch_and_save_html_content,
)

last_article_ids = set()

def parse_listing_data(html_content: str) -> Optional[tuple[List[Dict[str, Any]], List[Dict[str, Any]]]]:
    """从HTML内容中解析出新币上线信息,返回(articles, latest_articles)元组"""
    try:
        # 查找包含目标数据的script标签
        pattern = r'<script id="__APP_DATA" type="application/json".*?>(.*?)</script>'
        script_content = re.search(pattern, html_content, re.DOTALL)
        
        if not script_content:
            log_with_time("🔴 No APP_DATA script found")
            return None
            
        # 解析JSON数据
        json_data = json.loads(script_content.group(1))
        
        # 保存解析后的JSON数据到data目��
        json_path = DATA_DIR / LISTING_PARSED_FILE
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        log_with_time(f"Parsed JSON saved to {json_path}")

        # 查找包含 catalogDetail 的路由
        route_data = None
        for route_content in json_data['appState']['loader']['dataByRouteId'].values():
            if 'catalogDetail' in route_content:
                route_data = route_content
                break
                
        if not route_data:
            log_with_time("🔴 No route with catalogDetail found") 
            return None
            
        # 获取两个列表
        articles = route_data['catalogDetail']['articles']
        latest_articles = route_data.get('latestArticles', [])
        
        # 统一时间字段
        for article in latest_articles:
            article['releaseDate'] = article.pop('publishDate', 0)
            
        return articles, latest_articles
        
    except Exception as e:
        log_with_time(f"🔴 Error parsing listing data: {e}")
        return None

async def save_and_parse_listings() -> Optional[tuple[List[Dict[str, Any]], List[Dict[str, Any]]]]:
    """获取并解析上币公告数据"""
    log_with_time("Fetching and parsing listings...")
    response_text = await fetch_and_save_html_content(LISTING_API_URL, LISTING_RAW_FILE)
    if response_text is None:
        return None
    return parse_listing_data(response_text)

async def send_new_article_notifications(articles: List[Dict[str, Any]], 
                                       new_ids: set,
                                       is_initial: bool = False) -> None:
    """发送新文章通知"""
    for article in articles:
        if article['id'] in new_ids:
            formatted_date = datetime.fromtimestamp(
                article['releaseDate']/1000
            ).strftime('%Y-%m-%d %H:%M:%S')
            
            # 添加来源标记
            source = "Latest Articles" if 'catalogName' in article else "Listing"

            message = build_message(
                title=article['title'],
                release_date=formatted_date,
                link=build_article_link(article['id'], 'listing'),
                announcement_type=f"{source}",
                is_initial=is_initial
            )
            await send_message_async(message)

async def monitor() -> None:
    """监控新币上线公告"""
    global last_article_ids
    log_with_time("🟢 Starting Binance listing monitor...")
    
    while True:
        try:
            # 检查新文章
            result = await save_and_parse_listings()
            if result is None:
                log_with_time("🔴 No articles found in this check")
                await asyncio.sleep(MONITOR_INTERVAL)
                continue
                
            articles, latest_articles = result
            # 合并两个列表
            all_articles = articles + latest_articles
            
            # 获取所有文章的ID集合
            current_article_ids = {article['id'] for article in all_articles}
            
            # 首次执行时,只记录ID不推送
            if len(last_article_ids) == 0:
                log_with_time("🔴 First run, recording article IDs without notification")
                last_article_ids = current_article_ids
            
            # 找出新文章ID
            new_article_ids = current_article_ids - last_article_ids
            
            if new_article_ids:
                log_with_time(f"🟢 Found {len(new_article_ids)} new articles")
                # print all new articles
                for article in all_articles:
                    if article['id'] in new_article_ids:
                        log_with_time(f"🟢 Article: {article['title']}")
                is_initial = len(last_article_ids) == 0 and ALWAYS_NOTIFY
                await send_new_article_notifications(all_articles, new_article_ids, is_initial)
            else:
                log_with_time("No new articles found")
            
            # 更新上次的文章ID集合
            last_article_ids = current_article_ids
            
        except Exception as e:
            log_with_time(f"🔴 Error in monitor loop: {e}")
            await send_message_async(f"❌ Monitor Error: {str(e)}")
        
        await asyncio.sleep(MONITOR_INTERVAL)

if __name__ == "__main__":
    asyncio.run(monitor())
