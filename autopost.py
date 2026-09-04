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
        "Xadicha onamizning fidoyiligi (Qur'on va Hadis asosida)",
        "Fotima onamizning ko'z yoshlari va qanoati",
        "Ona va bola mehri: Tarixdan yig'latadigan qissa",
        "Sahobalar hayotidan sabr va iroda darsi",
        "Ilm yo'lidagi fozila ayollar"
    ],
    "Oila va Tarbiya": [
        "Ona duosining mo'jizasi va farzand tarbiyasi",
        "Er-xotin o'rtasidagi sof muhabbat (Hadis va Oyat)",
        "Oila totuvligi: Kechirimli bo'lish fazilati",
        "Jannatga yetaklovchi soliha ayol",
        "Erni rozi qilish: Ajr va mukofotlar",
        "Uyimizdagi farishtalar: Halol luqma va baraka"
    ],
    "Ruhiyat va Axloq": [
        "Qalb xotirjamligi: Zikr va istig'for",
        "Hasad va g'iybatdan uzoq toza qalb",
        "Sabrning shirin mevasi: Qiyinchilik ortidagi yengillik",
        "Shukur qiling: Allohning senga bergan ne'matlari",
        "Vaqt g'animat: Umrni qanday o'tkazyapmiz?",
        "Yaxshi gumon: Xatolarni kechirish ulug'ligi",
        "Qarindoshlik rishtalari va mehr-oqibat"
    ],
    "Ibodat va Qur'on": [
        "Jannat sog'inchi: Allohning va'dasi",
        "Namoz: Qalb jarohatlariga malham",
        "Tahajjud sirlari: Tungi ko'z yoshlar",
        "Qabul bo'ladigan duolar siri",
        "Allohning go'zal ismlaridan tafakkur",
        "Qur'on o'qilgan xonadonning nuri",
        "Tavba: Allohning kechirimli ekani"
    ],
    "Kun Hadisi va Oyati": [
        "Yurakni larzaga soluvchi Kun Hadisi va Oyati",
        "Insonni o'ylantiradigan qisqa Hadis va uning Oyatdagi tasdig'i",
        "Gunohlarga to'siq bo'luvchi Hadis va Oyat",
        "Qiyomat kunini eslatuvchi qo'rqinchli va umidli dalillar",
        "Allohning ruxmati haqida yig'latuvchi Hadis va Oyat"
    ]
}

def generate_text_gemini(model, kategoriya, mavzu):
    prompt = f"""Sen Islom dinini juda chuqur biladigan, samimiy va chiroyli so'zlaydigan olim(a)san. 
Vazifang mo'minalar va musulmonlar kanali uchun bitta juda QISQA, LONDAN, HIKMATLI va YURAKKA TEGADIGAN (ta'sirli, yig'latadigan) post tayyorlash.
Kategoriya: {kategoriya}
Bugungi mavzu: {mavzu}

QAT'IY QOIDALAR:
1. HECH QACHON salomlashma. TO'G'RIDAN-TO'G'RI mavzuni boshla.
2. Har bir postda albatta BITTADAN QUR'ON OYATI va BITTADAN SAHIH HADIS keltir (yoki faqat oyat/hadis, qaysi biri mos bo'lsa. Eng yaxshisi - ikkalasini bir-biriga bog'lab, chuqur ma'no chiqarib berish).
3. Oyat yoki Hadisni keltirganda kitoblardan ANIQLIK bilan dalil qilib yoz (Masalan: Imom Buxoriy rivoyati, Baqara surasi 152-oyat).
4. Matn qisqa, tushunarli va inson qalbini titratadigan darajada ta'sirli bo'lsin. Uzundan-uzoq leksiya qilmang.
5. Diktor o'qiganda juda chiroyli va ohangdor chiqishi uchun tinish belgilaridan o'rnida foydalan. Matn robotga umuman o'xshamasin!
6. Har safar mutlaqo YANGI ma'lumot topib yoz.
7. Post oxirida qisqagina, qalbni eritadigan duo bilan yakunla.
8. Faqat toza matn yozgin, emojilarni minimal ishlating, markdown (** , _) larni ishlatmang.
9. MAVZU NOMINI, SARLAVHANI va KATEGORIYANI UMUMAN YOZMA! To'g'ridan-to'g'ri faqat maqolani boshla (diktor darhol o'qishni boshlashi uchun).
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
        from normalizer import normalize_for_tts
        clean_text = normalize_for_tts(clean_text)
    except Exception as e:
        print("⚠️ Normalizer topilmadi yoki xato:", e)

    try:
        # Rate ni -10% qilib sekinlashtiramiz, emotsiya kuchayadi
        communicate = edge_tts.Communicate(clean_text, "uz-UZ-MadinaNeural", rate="-10%")
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

    # Matn yuborish o'chirib qo'yildi, faqat MP3 yuboriladi
    if audio_file:
        with open(audio_file, 'rb') as f:
            title_text = mavzu[:50] + "..." if len(mavzu) > 50 else mavzu
            send_telegram("sendAudio", 
                          data={'chat_id': CHANNEL_ID, 'title': title_text, 'performer': 'Madina (AI)'}, 
                          files={'audio': f})

    print("🎉 Barcha jarayon yakunlandi!")

if __name__ == "__main__":
    main()
