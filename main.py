import asyncio
import binanceListing
from datetime import datetime

def log_with_time(message):
    """打印带时间戳的消息"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

async def run_all_monitors():
    """并发运行所有监控任务"""
    try:
        # 创建三个监控任务
        listing_task = asyncio.create_task(binanceListing.monitor())
        
        log_with_time("All monitors started successfully")
        
        # 等待所有任务完成(实际上是无限循环)
        await asyncio.gather(
            listing_task,
        )
    except Exception as e:
        log_with_time(f"Error in main monitor: {e}")
        # 如果发生错误,等待一段时间后重启
        await asyncio.sleep(60)
        await run_all_monitors()

if __name__ == "__main__":
    log_with_time("Starting Binance announcement monitoring system...")
    try:
        asyncio.run(run_all_monitors())
    except KeyboardInterrupt:
        log_with_time("Monitoring system stopped by user")
    except Exception as e:
        log_with_time(f"Fatal error in monitoring system: {e}")
