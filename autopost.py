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
    
    # 20 dan ortiq turli xil islomiy, tarbiyaviy va oilaviy mavzular
    mavzular = [
        "Payg'ambarimiz (s.a.v) hayotlaridan oila va ayollarga go'zal muomala haqida ibratli voqea",
        "Qur'oni Karimdagi biror suraning yoki oyatning qisqacha go'zal tafsiri va bugungi kunga xulosasi",
        "Sahobiy ayollar (masalan, Xadicha onamiz, Oisha onamiz, Fotima onamiz) hayotidan ibratli hikoya",
        "Islomda farzand tarbiyasi: onaning mas'uliyati va go'zal nasihatlar",
        "Imom Navaviyning 40 hadisidan biri va uning bugungi hayotimizdagi o'rni",
        "Mo'mina ayolning hayosi, tili va go'zal axloqining fazilatlari",
        "Shukur qilishning fazilati va ne'matlarga qanoat haqida ta'sirli qissa",
        "G'iybat, hasad va yomon gumondan saqlanishning ruhiy va diniy ahamiyati",
        "Jannat ta'rifi va Allohning soliha ayollarga tayyorlagan mukofotlari",
        "Namozning inson ruhiyatiga, qalb xotirjamligiga va ro'zg'or barakasiga ta'siri",
        "Sabr qilishning fazilati: Qiyinchiliklar va sinovlar ortidan keladigan yengillik",
        "Islomda er-xotin huquqlari, o'zaro mehr va baxtli oila qurish sirlari",
        "Allohning go'zal ismlari (Asma ul-Husna) dan birining chuqur ma'nosi va hayotimizdagi o'rni",
        "Qadimgi ulamolar hayotidan ibratli hikmatlar va ularning ma'naviy sharhi",
        "Vaqtning qadri va islomda ayol kishi umrini qanday mazmunli o'tkazishi kerakligi",
        "Tungi ibodatlar va Tahajjud namozining mo'min qalbini nurga to'ldiruvchi fazilati",
        "Duo qilishning odoblari va qabul bo'ladigan duolarning siri",
        "Mehr-oqibat, ota-onaga yaxshilik va qarindoshlik rishtalarini bog'lashning fazilati",
        "Yaxshi gumonda bo'lish va insonlar xatosini kechirish, qalbni tozalashning ulug'ligi",
        "Tarixdagi buyuk islom olimlari onalarining farzand tarbiyasidagi qahramonliklari va yondashuvi",
        "Rizqning Allohdan ekanligi, halol rizq va uyimizdagi baraka omillari",
        "Qur'on o'qish va tinglashning fazilati, uning xonadonga olib kiradigan farištalari",
        "Islomda erning o'rni, unga itoat etish va hurmat ko'rsatishning ulug' fazilatlari",
        "Erini rozi qilgan ayolning darajasi va unga va'da qilingan jannat mukofotlari",
        "Oila totuvligi: Erga chiroyli muomala qilish va uning xizmatini e'zozlash",
        "Er-xotin o'rtasidagi muhabbat: Erining ko'nglini topish va uni har doim qo'llab-quvvatlash sirlari"
    ]
    tanlangan_mavzu = random.choice(mavzular)
    
    prompt = f"""Sen Islom dinini juda chuqur biladigan, samimiy va chiroyli so'zlaydigan ilm ahlisan. 
Sening vazifang mo'minalar, ayollar va umumiy musulmonlar kanali uchun bitta chiroyli post tayyorlash.
Bugungi maxsus mavzu: {tanlangan_mavzu}

Qoidalar:
1. Har safar mutlaqo YANGI va TAKRORLANMAS ma'lumot (boshqa hikoya, boshqa hadis, boshqa oyat) topib yoz. Oldingi yozganlaringni takrorlama.
2. Post matni juda samimiy, o'quvchining imonini ziyoda qiladigan, ibratli va tushunarli tilda bo'lsin.
3. Kerakli joylarda go'zal emojilardan (🌸, ✨, 📖, 🕌, 🤍) me'yorida foydalan.
4. Post oxirida albatta qandaydir chiroyli duo yoki xulosa bilan yakunla.
5. Post uzunligi Telegramga mos (taxminan 800-1500 belgi) bo'lsin.
6. Faqat toza matn yozgin, hech qanday qo'shimcha tushuntirish so'zlari (masalan, "Mana sizga post" kabi) kerak emas."""
    
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
