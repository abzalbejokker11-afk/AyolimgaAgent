import os
import sys
import time
import requests

# GitHub Actions'da workflow faylini o'zgartira olmasligimiz sababli, kutubxonani shu yerda o'rnatamiz
try:
    import edge_tts
except ImportError:
    print("⏳ edge-tts o'rnatilmoqda...")
    os.system(f"{sys.executable} -m pip install edge-tts")
    import edge_tts

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

QAT'IY QOIDALAR:
1. HECH QACHON salomlashma ("Assalomu alaykum", "Hurmatli obunachilar" kabi so'zlarsiz TO'G'RIDAN-TO'G'RI mavzuni boshla).
2. Matn robotga o'xshamasin! Diktor (notiq) o'qiganda juda chiroyli, ravon va ohangdor chiqishi uchun tinish belgilaridan (vergul, nuqta, tire) o'rnida va aniq foydalan. Qisqa va ta'sirli jumlalar tuz.
3. Haqiqiy va ishonchli isbotlar keltir (Aniq Qur'on oyatlari yoki Sahih hadislar). 
4. Mavzuga doir qilinmasligi kerak bo'lgan narsalar (gunohlar, xatolar) haqida ham ogohlantirib, to'g'ri yo'l ko'rsat.
5. Har safar mutlaqo YANGI ma'lumot topib yoz.
6. Post oxirida chiroyli duo yoki xulosa bilan yakunla.
7. Faqat toza matn yozgin, qo'shimcha izohlar kerak emas."""
    
    try:
        # API ga so'rov yuborish
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if not text:
            print("❌ Model bo'sh javob qaytardi.")
            sys.exit(1)
            
        print("✅ Post yaratildi! Rasm tayyorlanmoqda...")
        
        # Rasm uchun prompt yaratish
        img_prompt_req = f"Based on this islamic text, write a short and beautiful English prompt for an AI image generator (like Midjourney). The image should represent peace, islamic aesthetics, nature, or architecture. NO humans, NO faces. Just scenery or beautiful abstract concepts. Return ONLY the English prompt. Text: {text[:500]}"
        img_prompt_resp = model.generate_content(img_prompt_req)
        img_prompt = img_prompt_resp.text.strip()
        
        import urllib.parse
        encoded_prompt = urllib.parse.quote(img_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        # Rasmni yuklab olish
        img_data = requests.get(image_url).content
        with open("post_image.jpg", 'wb') as handler:
            handler.write(img_data)
        
        print("✅ Rasm tayyor! Audio tayyorlanmoqda (Madina ovozi)...")
        
        # Matnni tozalash (audio o'qiyotganda xalaqit bermasligi uchun)
        import re
        import asyncio
        import edge_tts
        
        # Emojilar va yulduzchalarni olib tashlash
        clean_text = re.sub(r'[*_]', '', text) # qalin va qiya yozuv belgilari
        audio_file = "post_audio.mp3"
        
        async def generate_audio():
            # Madina ovozi (Ayol kishi)
            communicate = edge_tts.Communicate(clean_text, "uz-UZ-MadinaNeural")
            await communicate.save(audio_file)
            
        asyncio.run(generate_audio())
        print("✅ Audio tayyor! Telegramga yuborilmoqda...")
        
        # Telegramga avval rasm yuborish
        url_photo = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open("post_image.jpg", 'rb') as photo:
            requests.post(url_photo, data={'chat_id': CHANNEL_ID}, files={'photo': photo})
            
        # Keyin matn yuborish
        url_text = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHANNEL_ID,
            "text": text
        }
        
        success = False
        for urinish in range(3):
            r = requests.post(url_text, json=payload).json()
            if r.get("ok"):
                success = True
                break
            else:
                print(f"⚠️ Telegram API da matn xatosi: {r.get('description')}")
                time.sleep(5)
                
        if success:
            print("✅ Matn yuborildi. Endi audio yuborilmoqda...")
            url_audio = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio"
            with open(audio_file, 'rb') as audio:
                files = {'audio': audio}
                data = {
                    'chat_id': CHANNEL_ID, 
                    'title': tanlangan_mavzu[:50] + "...", 
                    'performer': 'Madina (AI)'
                }
                for urinish in range(3):
                    r_audio = requests.post(url_audio, data=data, files=files).json()
                    if r_audio.get("ok"):
                        print("✅ Islomiy post, RASM va AUDIO kanalga muvaffaqiyatli yuborildi!")
                        break
                    else:
                        print(f"⚠️ Telegram API da audio xatosi: {r_audio.get('description')}")
                        time.sleep(5)
        else:
            print("❌ Post yuborish muvaffaqiyatsiz yakunlandi.")
            sys.exit(1)
                    
    except Exception as e:
        print(f"❌ Gemini API yoki tarmoqda xatolik: {e}")
        sys.exit(1)

if __name__ == "__main__":
    post_yuborish()
