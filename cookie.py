import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from typing import Optional, Dict, List

class CookieManager:
    def __init__(self, cookie_file: str = "cookies.txt"):
        """初始化CookieManager
        
        Args:
            cookie_file: cookie文件路径
        """
        self.cookie_file = Path(cookie_file)
        self.cookie_str: Optional[str] = None
        self._load_cookies()

    def _load_cookies(self) -> None:
        """从文件加载cookie"""
        try:
            if self.cookie_file.exists():
                self.cookie_str = self.cookie_file.read_text().strip()
                self._log(f"📥 Loaded cookies from {self.cookie_file}")
        except Exception as e:
            self._log(f"❌ Failed to load cookies: {e}")

    def _save_cookies(self) -> None:
        """保存cookie到文件"""
        try:
            self.cookie_file.write_text(self.cookie_str)
            self._log(f"📤 Saved cookies to {self.cookie_file}")
        except Exception as e:
            self._log(f"❌ Failed to save cookies: {e}")

    async def update_cookies(self) -> str:
        """使用playwright获取新的cookie
        
        Returns:
            str: 新的cookie字符串
        """
        self._log("🔄 Starting to fetch new cookies...")
        
        async with async_playwright() as p:
            # 配置启动参数以支持Docker环境
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            try:
                page = await browser.new_page()
                await page.goto('https://www.binance.com/en/support/announcement/new-cryptocurrency-listing')
                await page.wait_for_load_state('networkidle')
                
                cookies = await page.context.cookies()
                self.cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
                
                # 保存新cookie到文件
                self._save_cookies()
                
                self._log("✅ Successfully fetched new cookies")
                return self.cookie_str
                
            except Exception as e:
                self._log(f"❌ Failed to fetch cookies: {e}")
                raise
            finally:
                await browser.close()

    def get_cookies(self) -> Optional[str]:
        """获取当前cookie
        
        Returns:
            Optional[str]: cookie字符串,如果没有则返回None
        """
        return self.cookie_str

    def _log(self, message: str) -> None:
        """输出日志
        
        Args:
            message: 日志消息
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{current_time}] {message}")

async def main():
    """测试代码"""
    cookie_manager = CookieManager()
    
    # 获取现有cookie
    current_cookies = cookie_manager.get_cookies()
    print(f"Current cookies: {current_cookies and current_cookies[:100]}...")
    
    # 更新cookie
    new_cookies = await cookie_manager.update_cookies()
    print(f"New cookies: {new_cookies[:100]}...")

if __name__ == "__main__":
    asyncio.run(main()) 
