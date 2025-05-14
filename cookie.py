import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from typing import Optional, Dict, List

from config import USE_PROXY, PROXY_URL

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
                    headless=False,  # 设置为False以便你看到并手动完成验证
                    proxy={"server": PROXY_URL} if USE_PROXY else None  # 根据配置使用代理
                )
                context = await browser.new_context()
                page = await context.new_page()
                
                # 访问币安网站
                await page.goto("https://www.binance.com/en/support/announcement/list/48?navId=48")
                
                # 等待加载完成
                await page.wait_for_load_state("networkidle")
                
                # 检查是否需要验证
                if await page.title() == "Human Verification" or "captcha" in await page.content():
                    self._log("检测到人机验证，请在浏览器中手动完成验证...")
                    
                    # 使用event_listener替代wait_for_navigation
                    verification_completed = asyncio.Event()
                    
                    # 监听导航事件
                    async def on_navigation(response):
                        if response.url.startswith("https://www.binance.com/en/support/announcement"):
                            # 如果导航到了公告页面，说明验证完成了
                            verification_completed.set()
                    
                    page.on("response", on_navigation)
                    
                    # 等待用户完成验证
                    try:
                        await asyncio.wait_for(verification_completed.wait(), timeout=120)
                    except asyncio.TimeoutError:
                        self._log("验证超时，请重试")
                        await browser.close()
                        return self.cookies
                    
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

async def get_binance_cookie():
    """打开浏览器获取币安Cookie"""
    print("正在启动浏览器获取币安Cookie...")
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=False,  # 设置为False以便你看到并手动完成验证
            proxy={"server": PROXY_URL} if USE_PROXY else None  # 使用配置中的代理
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 访问币安网站
            print("正在打开币安公告页面...")
            await page.goto("https://www.binance.com/en/support/announcement/list/48?navId=48")
            
            # 等待加载完成
            await page.wait_for_load_state("networkidle")
            
            # 检查是否需要验证
            if await page.title() == "Human Verification" or "captcha" in await page.content():
                print("检测到人机验证，请在浏览器中手动完成验证...")
                print("完成验证后，请等待页面自动加载完成...")
                
                # 创建一个事件以等待导航完成
                verification_completed = asyncio.Event()
                
                # 监听导航事件
                async def on_response(response):
                    if response.url.startswith("https://www.binance.com/en/support/announcement"):
                        if response.status == 200:
                            verification_completed.set()
                
                page.on("response", on_response)
                
                # 等待用户完成验证
                try:
                    print("等待验证完成，最多等待2分钟...")
                    await asyncio.wait_for(verification_completed.wait(), timeout=120)
                    print("✅ 验证完成！")
                except asyncio.TimeoutError:
                    print("❌ 验证超时，请重试")
                    await browser.close()
                    return None
                
                # 等待页面稳定
                await page.wait_for_load_state("networkidle")
            else:
                print("✅ 页面正常加载，无需验证")
            
            # 等待一会儿，确保所有cookie都已设置
            await asyncio.sleep(2)
            
            # 获取cookies
            cookies = await context.cookies()
            
            # 将cookies格式化为字符串
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            
            # 保存到文件
            with open("cookies.txt", "w") as f:
                f.write(cookie_str)
            
            print(f"✅ Cookie已保存到cookies.txt")
            print(f"Cookie前50个字符: {cookie_str[:50]}...")
            
            print("请关闭浏览器窗口...")
            
            # 给用户一些时间查看结果
            await asyncio.sleep(3)
            await browser.close()
            
            return cookie_str
            
        except Exception as e:
            print(f"❌ 获取Cookie过程中出错: {e}")
            await browser.close()
            return None

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(get_binance_cookie()) 