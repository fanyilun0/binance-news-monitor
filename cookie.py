import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from typing import Optional, Dict, List

from config import USE_PROXY

class CookieManager:
    """管理和更新Cookie"""
    
    def __init__(self, cookie_file='cookies.txt'):
        """初始化Cookie管理器"""
        self.cookie_file = cookie_file
        self.cookie_path = Path(cookie_file)
        self.cookies = None
        self.last_update = None
        
        # 如果cookie文件存在，立即加载
        if self.cookie_path.exists():
            self._load_cookies()

    def _load_cookies(self):
        """从文件加载cookies"""
        try:
            if self.cookie_path.exists():
                with open(self.cookie_path, 'r') as f:
                    self.cookies = f.read().strip()
                self.last_update = datetime.now()
                return True
            return False
        except Exception as e:
            print(f"Error loading cookies: {e}")
            return False

    def _save_cookies(self):
        """保存cookies到文件"""
        try:
            with open(self.cookie_path, 'w') as f:
                f.write(self.cookies)
            return True
        except Exception as e:
            print(f"Error saving cookies: {e}")
            return False

    def get_cookies(self):
        """获取当前cookies"""
        if not self.cookies:
            self._load_cookies()
        return self.cookies

    def update_cookie_from_str(self, cookie_str):
        """从字符串更新cookie"""
        if not cookie_str:
            return False
            
        self.cookies = cookie_str
        self.last_update = datetime.now()
        return self._save_cookies()

    async def update_cookies(self):
        """通过Playwright自动获取新的cookies"""
        self._log("尝试使用浏览器自动获取新Cookie...")
        
        try:
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(
                    headless=False,  # 设置为True可隐藏浏览器窗口，但可能导致验证失败
                    proxy={"server": "http://localhost:7890"} if USE_PROXY else None
                )
                context = await browser.new_context()
                page = await context.new_page()
                
                # 访问币安网站
                await page.goto("https://www.binance.com/en/support/announcement/list/48?navId=48")
                
                # 等待加载完成
                await page.wait_for_load_state("networkidle")
                
                # 检查是否需要验证
                if await page.title() == "Human Verification" or "captcha" in await page.content():
                    self._log("检测到人机验证，请在弹出的浏览器中手动完成验证...")
                    
                    # 等待用户完成验证并加载新页面
                    await page.wait_for_navigation(timeout=120000)  # 给用户2分钟时间完成验证
                    
                    # 等待页面稳定
                    await page.wait_for_load_state("networkidle")
                
                # 获取cookies
                cookies = await context.cookies()
                
                # 将cookies格式化为字符串
                cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                
                # 保存到文件和内存
                self.cookies = cookie_str
                self.last_update = datetime.now()
                self._save_cookies()
                
                await browser.close()
                
                self._log("✅ 成功更新Cookie")
                return self.cookies
                
        except Exception as e:
            self._log(f"❌ 自动获取Cookie失败: {e}")
            
            # 尝试重新加载cookie文件作为备选方案
            success = self._load_cookies()
            if not success:
                self._log("无法更新cookie，请手动更新cookie.txt文件")
            
            return self.cookies

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