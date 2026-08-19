import os
import sys
import asyncio
import random
import re
import requests
import google.generativeai as genai
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, BotCommand, FSInputFile
from aiogram.filters import Command
import edge_tts

CHANNEL_ID = "-1004422906049"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "BU_YERGA_TOKEN_YOZING")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "BU_YERGA_KALIT_YOZING")

router = Router()

async def generate_and_send_post(bot: Bot, chat_id: int, task_type: str):
    import requests
    url = "https://api.github.com/repos/abzalbejokker11-afk/AyolimgaAgent/actions/workflows/post.yml/dispatches"
    
    GH_TOKEN = os.environ.get("GH_TOKEN", "BU_YERGA_TOKEN_YOZING")
    
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "ref": "main"
    }
    
    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code == 204:
            await bot.send_message(chat_id, "✅ Buyruq bulutli serverga (GitHub Actions) yuborildi!\n\nBu jarayon taxminan 30-40 soniya oladi. Tayyor bo'lgach avtomatik kanalga tushadi. (Render xatoliklari aylanib o'tildi!)")
        else:
            await bot.send_message(chat_id, f"⚠️ Bulutli serverga ulanishda muammo: {r.status_code}\n{r.text}")
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Xatolik yuz berdi: {e}")

@router.message(Command("post"))
async def cmd_post(message: Message, bot: Bot):
    await generate_and_send_post(bot, message.chat.id, "post")

@router.message(Command("hadis"))
async def cmd_hadis(message: Message, bot: Bot):
    await generate_and_send_post(bot, message.chat.id, "hadis")

@router.message(Command("oila"))
async def cmd_oila(message: Message, bot: Bot):
    await generate_and_send_post(bot, message.chat.id, "oila")

@router.message(Command("quron"))
async def cmd_quron(message: Message, bot: Bot):
    await generate_and_send_post(bot, message.chat.id, "quron")

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="post", description="📝 Tasodifiy post yaratish"),
        BotCommand(command="hadis", description="📜 Hadis bo'yicha post tayyorlash"),
        BotCommand(command="oila", description="👨‍👩‍👧‍👦 Oila haqida post tayyorlash"),
        BotCommand(command="quron", description="📖 Qur'on oyatlari sharhi")
    ]
    await bot.set_my_commands(commands)

async def main():
    if TELEGRAM_TOKEN == "BU_YERGA_TOKEN_YOZING":
        print("❌ Iltimos, TELEGRAM_TOKEN ni kiriting!")
        sys.exit(1)
        
    import keep_alive
    keep_alive.keep_alive()
        
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(router)
    await set_bot_commands(bot)
    
    print("✅ Aiogram Bot ishga tushdi. Bot xabarlarni kutmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
