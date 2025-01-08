import asyncio
import aiohttp
from playwright.async_api import async_playwright
from config import COINGLASS_URL, WEBHOOK_URL, COINGLASS_FILE_INTERVAL
from util import log_with_time
import os
import hashlib
import base64


class CoinglassScraper:
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
    
    async def _initialize(self):
        """初始化浏览器"""
        if not self._browser:
            try:
                playwright = await async_playwright().start()
                self._browser = await playwright.chromium.launch(headless=True)
                self._context = await self._browser.new_context()
                self._page = await self._context.new_page()
            except Exception as e:
                log_with_time(f"❌ 初始化浏览器失败: {str(e)}")
    
    async def _close(self):
        """关闭浏览器"""
        if self._browser:
            try:
                await self._browser.close()
                self._browser = None
                self._context = None
                self._page = None
            except Exception as e:
                log_with_time(f"❌ 关闭浏览器失败: {str(e)}")
    
    async def _download_and_send_image(self):
        """下载并发送图片到webhook"""
        try:
            log_with_time("🟢 开始访问 Coinglass 网页...")
            await self._page.goto(COINGLASS_URL)
            await self._page.wait_for_selector('table', timeout=30000)
            
            download_button = await self._page.wait_for_selector('.MuiButton-variantOutlined', timeout=30000)
            
            download = None
            async with self._page.expect_download() as download_info:
                await download_button.click()
                download = await download_info.value
            
            if download:
                os.makedirs('./downloads', exist_ok=True)
                save_path = os.path.join('./downloads', 'peak_signals.png')
                await download.save_as(save_path)
                log_with_time(f"🟢 图片已保存到: {save_path}")
                
                try:
                    await self._send_image_to_webhook(save_path)
                    log_with_time("🟢 图片发送成功!")
                finally:
                    if os.path.exists(save_path):
                        os.remove(save_path)
                        log_with_time("🟢 临时文件已清理")
            else:
                log_with_time("❌ 下载图片失败")
            
        except Exception as e:
            log_with_time(f"❌ 下载和发送图片失败: {str(e)}")
    
    async def _send_image_to_webhook(self, image_path):
        """发送图片到企业微信webhook"""
        try:
            with open(image_path, 'rb') as f:
                image_content = f.read()
            
            md5 = hashlib.md5(image_content).hexdigest()
            base64_content = base64.b64encode(image_content).decode('utf-8')
            
            payload = {
                "msgtype": "image",
                "image": {
                    "base64": base64_content,
                    "md5": md5
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            proxy = None
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(WEBHOOK_URL, 
                                          json=payload, 
                                          headers=headers, 
                                          proxy=proxy) as response:
                        if response.status != 200:
                            log_with_time(f"❌ 发送图片失败: {response.status}")
                            
            except Exception as e:
                log_with_time(f"❌ 发送请求时出错: {str(e)}")
                raise
                
        except Exception as e:
            log_with_time(f"❌ 发送图片时出错: {str(e)}")
            raise

if __name__ == "__main__":
    async def main():
        while True:
            scraper = CoinglassScraper()
            try:
                await scraper._initialize()
                log_with_time("开始获取和比较数据...")
                await scraper._download_and_send_image()
                await asyncio.sleep(COINGLASS_FILE_INTERVAL)
            except Exception as e:
                log_with_time(f"运行失败: {str(e)}")
            finally:
                await scraper._close()
    
    asyncio.run(main())