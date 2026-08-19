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
    await bot.send_message(chat_id, f"⏳ '{task_type}' bo'yicha post va audio tayyorlanmoqda. Bu biroz vaqt olishi mumkin...")
    
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-3.5-flash')
    
    if task_type == "hadis":
        tanlangan_mavzu = "Imom Navaviyning 40 hadisidan biri yoki Payg'ambarimizning (s.a.v) go'zal hadislaridan biri va uning sharhi"
    elif task_type == "oila":
        tanlangan_mavzu = "Islomda oila totuvligi, er-xotin huquqlari, erga hurmat, farzand tarbiyasi haqida"
    elif task_type == "quron":
        tanlangan_mavzu = "Qur'oni Karimdagi ibratli bir oyat yoki suraning qisqacha go'zal tafsiri va xulosasi"
    else:
        mavzular = [
            "Payg'ambarimiz (s.a.v) hayotlaridan oila va ayollarga go'zal muomala haqida ibratli voqea",
            "Sahobiy ayollar (masalan, Xadicha onamiz, Oisha onamiz, Fotima onamiz) hayotidan ibratli hikoya",
            "Mo'mina ayolning hayosi, tili va go'zal axloqining fazilatlari",
            "Shukur qilishning fazilati va ne'matlarga qanoat haqida ta'sirli qissa",
            "Jannat ta'rifi va Allohning soliha ayollarga tayyorlagan mukofotlari",
            "Duo qilishning odoblari va qabul bo'ladigan duolarning siri",
            "Mehr-oqibat, ota-onaga yaxshilik va qarindoshlik rishtalarini bog'lashning fazilati"
        ]
        tanlangan_mavzu = random.choice(mavzular)

    prompt = f"""Sen Islom dinini juda chuqur biladigan, samimiy va chiroyli so'zlaydigan ilm ahlisan. 
Sening vazifang mo'minalar, ayollar va umumiy musulmonlar kanali uchun bitta chiroyli post tayyorlash.
Bugungi maxsus mavzu: {tanlangan_mavzu}

Qoidalar:
1. Har safar mutlaqo YANGI va TAKRORLANMAS ma'lumot (boshqa hikoya, boshqa hadis, boshqa oyat) topib yoz.
2. Post matni juda samimiy, o'quvchining imonini ziyoda qiladigan, ibratli va tushunarli tilda bo'lsin.
3. Kerakli joylarda go'zal emojilardan me'yorida foydalan.
4. Post oxirida albatta qandaydir chiroyli duo yoki xulosa bilan yakunla.
5. Post uzunligi Telegramga mos (taxminan 800-1500 belgi) bo'lsin.
6. Faqat toza matn yozgin, qo'shimcha so'zlar kerak emas."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if not text:
            await bot.send_message(chat_id, "❌ Model bo'sh javob qaytardi.")
            return

        await bot.send_message(chat_id, "✅ Matn yaratildi. Audio tayyorlanmoqda (Madina ovozi)...")
        
        clean_text = re.sub(r'[*_]', '', text)
        audio_file = "post_audio.mp3"
        communicate = edge_tts.Communicate(clean_text, "uz-UZ-MadinaNeural")
        await communicate.save(audio_file)
        
        await bot.send_message(chat_id, "✅ Audio tayyor! Kanalga yuborilmoqda...")
        
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")
        
        audio_input = FSInputFile(audio_file)
        await bot.send_audio(
            chat_id=CHANNEL_ID, 
            audio=audio_input, 
            title=tanlangan_mavzu[:50] + "...", 
            performer="Madina (AI)"
        )
        
        await bot.send_message(chat_id, "🎉 Post va Audio muvaffaqiyatli kanalga yuborildi!")
        
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
