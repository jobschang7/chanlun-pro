import asyncio
from telegram import Bot
import config  # 确保导入了config模块

# 创建Telegram Bot实例
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

async def send_telegram_message(message: str):
    """发送Telegram消息"""
    await bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=message)

# 测试发送Telegram消息
async def main():
    await send_telegram_message("Hello, this is a test message to the Telegram group!")

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main())
