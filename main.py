import asyncio
import binanceListing
import coinglass
from datetime import datetime
from config import ENABLE_COINGLASS, COINGLASS_FILE_INTERVAL
def log_with_time(message):
    """打印带时间戳的消息"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

async def run_coinglass_monitor():
    """运行 Coinglass 监控"""
    if not ENABLE_COINGLASS:
        return
    while True:
        scraper = coinglass.CoinglassScraper()
        try:
            await scraper._initialize()
            log_with_time("🟢 开始 Coinglass 指标监控...")
            await scraper._download_and_send_image()
            log_with_time(f"🟢 Coinglass 监控完成,等待 {COINGLASS_FILE_INTERVAL} 秒后重新检查...")
            await asyncio.sleep(COINGLASS_FILE_INTERVAL)
        except Exception as e:
            log_with_time(f"❌ Coinglass 监控错误: {e}")
            await asyncio.sleep(60)
        finally:
            await scraper._close()

async def run_all_monitors():
    """并发运行所有监控任务"""
    try:
        # 创建监控任务
        listing_task = asyncio.create_task(binanceListing.monitor())
        coinglass_task = asyncio.create_task(run_coinglass_monitor())
        
        log_with_time("🟢 所有监控任务启动成功")
        
        # 等待所有任务完成
        await asyncio.gather(
            listing_task,
            coinglass_task
        )
    except Exception as e:
        log_with_time(f"❌ 主监控错误: {e}")
        # 如果发生错误,等待一段时间后重启
        await asyncio.sleep(60)
        await run_all_monitors()

if __name__ == "__main__":
    log_with_time("🟢 启动币安公告监控系统...")
    try:
        asyncio.run(run_all_monitors())
    except KeyboardInterrupt:
        log_with_time("🟢 监控系统被用户停止")
    except Exception as e:
        log_with_time(f"❌ 监控系统致命错误: {e}")
