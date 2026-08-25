import os
import sys
import time
import requests
import datetime
import random
import re
import urllib.parse
import asyncio

# GitHub Actions uchun dinamik o'rnatish
try:
    import edge_tts
except ImportError:
    print("⏳ edge-tts o'rnatilmoqda...")
    os.system(f"{sys.executable} -m pip install edge-tts")
    import edge_tts

import google.generativeai as genai

CHANNEL_ID = "-1004422906049"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "BU_YERGA_TOKEN_YOZING")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "BU_YERGA_KALIT_YOZING")

MAVZULAR_BAZASI = {
    "Tarix va Ibrat": [
        "Payg'ambarimiz (s.a.v) hayotlaridan oila va ayollarga go'zal muomala haqida ibratli voqea",
        "Sahobiy ayollar (Xadicha, Oisha, Fotima onalarimiz) hayotidan hikmatli qissa",
        "Qadimgi islom ulamolari va ularning onalari o'rtasidagi go'zal mehr-oqibat",
        "Tarixdagi buyuk islom olimlari onalarining farzand tarbiyasidagi qahramonliklari",
        "Islom tarixida ilm tarqatgan fozila ayollar haqida"
    ],
    "Oila va Tarbiya": [
        "Islomda farzand tarbiyasi: onaning mas'uliyati va go'zal nasihatlar",
        "Islomda er-xotin huquqlari, o'zaro mehr va baxtli oila qurish sirlari",
        "Oila totuvligi: Erga chiroyli muomala qilish va uning xizmatini e'zozlash",
        "Erini rozi qilgan ayolning darajasi va unga va'da qilingan jannat mukofotlari",
        "Islomda erning o'rni, unga itoat etish va hurmat ko'rsatishning ulug' fazilatlari",
        "Er-xotin o'rtasidagi muhabbat: ko'ngil topish va doimiy qo'llab-quvvatlash"
    ],
    "Ruhiyat va Axloq": [
        "Mo'mina ayolning hayosi, tili va go'zal axloqining fazilatlari",
        "Shukur qilishning fazilati va ne'matlarga qanoat haqida ta'sirli qissa",
        "G'iybat, hasad va yomon gumondan saqlanishning ruhiy va diniy ahamiyati",
        "Sabr qilishning fazilati: Qiyinchiliklar va sinovlar ortidan keladigan yengillik",
        "Vaqtning qadri va islomda ayol kishi umrini qanday mazmunli o'tkazishi kerakligi",
        "Yaxshi gumonda bo'lish, insonlar xatosini kechirish va qalbni tozalashning ulug'ligi",
        "Mehr-oqibat, ota-onaga yaxshilik va qarindoshlik rishtalarini bog'lashning fazilati"
    ],
    "Ibodat va Qur'on": [
        "Qur'oni Karimdagi biror suraning yoki oyatning qisqacha go'zal tafsiri",
        "Imom Navaviyning 40 hadisidan biri va uning bugungi hayotimizdagi o'rni",
        "Jannat ta'rifi va Allohning soliha ayollarga tayyorlagan mukofotlari",
        "Namozning inson ruhiyatiga, qalb xotirjamligiga va ro'zg'or barakasiga ta'siri",
        "Allohning go'zal ismlari (Asma ul-Husna) dan birining hayotimizdagi o'rni",
        "Tungi ibodatlar va Tahajjud namozining mo'min qalbini nurga to'ldiruvchi fazilati",
        "Duo qilishning odoblari va qabul bo'ladigan duolarning siri",
        "Qur'on o'qish va tinglashning fazilati, uning xonadonga olib kiradigan farishtalari",
        "Rizqning Allohdan ekanligi, halol rizq va uyimizdagi baraka omillari"
    ]
}

def generate_text_gemini(model, kategoriya, mavzu):
    prompt = f"""Sen Islom dinini juda chuqur biladigan, samimiy va chiroyli so'zlaydigan olim(a)san. 
Sening vazifang mo'minalar va umumiy musulmonlar kanali uchun bitta juda ta'sirli, chiroyli post tayyorlash.
Kategoriya: {kategoriya}
Bugungi mavzu: {mavzu}

QAT'IY QOIDALAR:
1. HECH QACHON salomlashma ("Assalomu alaykum", "Hurmatli obunachilar" kabi so'zlarsiz TO'G'RIDAN-TO'G'RI mavzuni boshla).
2. Matn robotga o'xshamasin! Diktor o'qiganda juda chiroyli, ravon va ohangdor chiqishi uchun tinish belgilaridan (vergul, nuqta, tire) o'rnida va aniq foydalan.
3. Haqiqiy va ishonchli isbotlar keltir (Aniq Qur'on oyatlari, sura nomlari yoki Sahih hadislar). 
4. Odamlar hayotida uchraydigan xatolar va ulardan qanday saqlanish kerakligi haqida chuqur ibratli xulosalar ber.
5. Har safar mutlaqo YANGI ma'lumot topib yoz. Eskirgan yoki yod bo'lib ketgan gaplarni qaytarma.
6. Post oxirida chiroyli duo bilan yakunla.
7. Faqat toza matn yozgin, qo'shimcha izohlar, emojilar va formatlash belgilari (**, _) ni minimal darajada ishlat yoki umuman ishlatma.
"""
    
    for urinish in range(3):
        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text.strip()
        except Exception as e:
            print(f"⚠️ Matn yaratishda xato (urinish {urinish+1}): {e}")
            time.sleep(3)
    return None

def generate_image_pollinations(model, text):
    prompt_req = f"""Based on this islamic text, write a short, vivid, and highly descriptive English prompt for an AI image generator (like Midjourney). 
The image should be breathtaking, peaceful, high quality (8k, unreal engine, cinematic lighting).
Theme: Islamic aesthetics, nature, abstract peace, or beautiful architecture.
CRITICAL RULE: NO humans, NO faces, NO text in the image. Just scenery, geometry, or abstract beauty.
Return ONLY the English prompt string. Text to base it on: {text[:500]}"""
    
    try:
        resp = model.generate_content(prompt_req)
        img_prompt = resp.text.strip()
        encoded = urllib.parse.quote(img_prompt)
        # Using pollination AI
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
        
        r = requests.get(image_url, timeout=15)
        if r.status_code == 200:
            file_name = "post_image.jpg"
            with open(file_name, 'wb') as f:
                f.write(r.content)
            return file_name
    except Exception as e:
        print(f"⚠️ Rasm yaratishda xato: {e}")
    return None

async def generate_audio_edge(text):
    file_name = "post_audio.mp3"
    # Tozalash
    clean_text = re.sub(r'[*_#]', '', text)
    try:
        communicate = edge_tts.Communicate(clean_text, "uz-UZ-MadinaNeural")
        await communicate.save(file_name)
        return file_name
    except Exception as e:
        print(f"⚠️ Audio yaratishda xato: {e}")
    return None

def send_telegram(method, data, files=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    for urinish in range(3):
        try:
            if files:
                r = requests.post(url, data=data, files=files, timeout=60).json()
            else:
                r = requests.post(url, json=data, timeout=30).json()
            
            if r.get("ok"):
                return True
            else:
                print(f"⚠️ Telegram API Xato ({method}): {r.get('description')}")
        except Exception as e:
            print(f"⚠️ Telegram API Ulanish Xatosi ({method}): {e}")
        time.sleep(5)
    return False

def main():
    if TELEGRAM_TOKEN == "BU_YERGA_TOKEN_YOZING" or GEMINI_KEY == "BU_YERGA_KALIT_YOZING":
        print("❌ Tokenlar kiritilmagan!")
        sys.exit(1)

    is_manual = os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
    
    if not is_manual:
        print("🛑 Ushbu post GitHub Cron orqali keldi. Render API nazoratida bo'lgani uchun to'xtatildi.")
        sys.exit(0)

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    print(f"🚀 Dastur ishga tushdi... Soat: {now.hour}:{now.minute}")

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-3.5-flash')

    kategoriya = random.choice(list(MAVZULAR_BAZASI.keys()))
    mavzu = random.choice(MAVZULAR_BAZASI[kategoriya])
    print(f"📖 Kategoriya: {kategoriya} | Mavzu: {mavzu}")

    # 1. Matn
    text = generate_text_gemini(model, kategoriya, mavzu)
    if not text:
        print("❌ Matn yaratib bo'lmadi.")
        sys.exit(1)
    print("✅ Matn tayyor!")

    # 2. Rasm
    img_file = generate_image_pollinations(model, text)
    if img_file:
        print("✅ Rasm tayyor!")
    else:
        print("⚠️ Rasm tayyorlanmadi, davom etamiz.")

    # 3. Audio
    audio_file = asyncio.run(generate_audio_edge(text))
    if audio_file:
        print("✅ Audio tayyor!")
    else:
        print("⚠️ Audio tayyorlanmadi, davom etamiz.")

    # 4. Telegramga yuborish
    if img_file:
        with open(img_file, 'rb') as f:
            send_telegram("sendPhoto", data={'chat_id': CHANNEL_ID}, files={'photo': f})

    text_success = send_telegram("sendMessage", data={'chat_id': CHANNEL_ID, 'text': text})
    
    if text_success and audio_file:
        with open(audio_file, 'rb') as f:
            title_text = mavzu[:50] + "..."
            send_telegram("sendAudio", 
                          data={'chat_id': CHANNEL_ID, 'title': title_text, 'performer': 'Madina (AI)'}, 
                          files={'audio': f})

    print("🎉 Barcha jarayon yakunlandi!")

if __name__ == "__main__":
    main()
