import os
import sys
import time
import requests
import google.generativeai as genai
import random

# Telegram kanalingiz ID si (Odatda Telegram kanallar oldida -100 bo'ladi, agar ishlamasa -100 siz yozib ko'rasiz)
CHANNEL_ID = "-1004422906049"

# Tokenlar (Maxfiy muhit o'zgaruvchilaridan olinadi)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "BU_YERGA_TOKEN_YOZING")
GEMINI_KEY     = os.environ.get("GEMINI_KEY", "BU_YERGA_KALIT_YOZING")

if TELEGRAM_TOKEN == "BU_YERGA_TOKEN_YOZING" or GEMINI_KEY == "BU_YERGA_KALIT_YOZING":
    print("❌ Xato: TELEGRAM_TOKEN yoki GEMINI_KEY muhit o'zgaruvchilarida topilmadi!")
    sys.exit(1)

def post_yuborish():
    print("⏳ Islomiy post yaratilmoqda...")
    genai.configure(api_key=GEMINI_KEY)
    
    # Eng yaxshi va barqaror model
    model = genai.GenerativeModel('gemini-3.5-flash')
    
    # 3 xil mavzudan birini tasodifiy tanlaymiz
    mavzular = [
        "Imom Navaviyning 40 hadisi va ularning chuqur ruhiy sharhi",
        "Qur'oni Karimdagi biror suraning qisqacha go'zal tafsiri va hayotiy xulosalar",
        "Payg'ambarimiz (s.a.v) yoki sahobalar hayotidan ibratli hikoya va undan olinadigan dars"
    ]
    tanlangan_mavzu = random.choice(mavzular)
    
    prompt = f"""Sen Islom dinini juda chuqur biladigan, samimiy va chiroyli so'zlaydigan ilm ahlisan. 
Sening vazifang mo'minalar, ayollar va umumiy musulmonlar kanali uchun bitta chiroyli post tayyorlash.
Post mavzusi: {tanlangan_mavzu}

Qoidalar:
1. Post matni juda samimiy, o'quvchining imonini ziyoda qiladigan, ibratli va tushunarli tilda bo'lsin.
2. Kerakli joylarda go'zal emojilardan (🌸, ✨, 📖, 🕌, 🤍) me'yorida foydalan.
3. Post oxirida albatta qandaydir chiroyli duo yoki xulosa bilan yakunla.
4. Post uzunligi Telegramga mos (taxminan 800-1500 belgi) bo'lsin.
5. Faqat toza matn yozgin, hech qanday qo'shimcha tushuntirish so'zlari (masalan, "Mana sizga post" kabi) kerak emas."""
    
    try:
        # API ga so'rov yuborish
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if not text:
            print("❌ Model bo'sh javob qaytardi.")
            sys.exit(1)
            
        print("✅ Post yaratildi! Telegramga yuborilmoqda...")
        
        # Telegramga faqat matn yuborish (ayol kishi kanali uchun kitobiy va sokinroq)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML" # Yoki Markdown
        }
        
        # Internet xatolarining oldini olish uchun 3 marta urinib ko'ramiz
        for urinish in range(3):
            r = requests.post(url, json=payload).json()
            if r.get("ok"):
                print("✅ Islomiy post kanalga muvaffaqiyatli yuborildi!")
                break
            else:
                print(f"⚠️ Telegram API da xato: {r.get('description')}")
                if urinish < 2:
                    print("Qayta urinib ko'rilmoqda...")
                    time.sleep(5)
                else:
                    print("❌ Post yuborish muvaffaqiyatsiz yakunlandi.")
                    sys.exit(1)
                    
    except Exception as e:
        print(f"❌ Gemini API yoki tarmoqda xatolik: {e}")
        sys.exit(1)

if __name__ == "__main__":
    post_yuborish()
