import os
from flask import Flask
from threading import Thread
import time
import requests
import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

@app.route("/test_tts")
def test_tts():
    import asyncio
    import edge_tts
    import requests
    try:
        # Fetch a free proxy
        r = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt")
        proxies = r.text.strip().split('\n')
        # Try a few proxies
        async def run_tts():
            for p in proxies[10:20]:  # pick some random ones
                proxy = f"http://{p.strip()}"
                try:
                    comm = edge_tts.Communicate("Salom", "uz-UZ-MadinaNeural", proxy=proxy)
                    await comm.save("test.mp3")
                    return f"Success with {proxy}"
                except Exception as e:
                    continue
            raise Exception("All proxies failed")
            
        res = asyncio.run(run_tts())
        return res
    except Exception as e:
        return f"TTS Failed: {e}"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def schedule_posts():
    while True:
        try:
            # O'zbekiston vaqti
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
            # Soat 07:00, 08:00 yoki 10:00 va daqiqa 0 bo'lsa
            if now.hour in [7, 8, 10] and now.minute == 0:
                print(f"⏰ Rejalashtirilgan vaqt! {now.hour}:00 - GitHub ga signal yuborilmoqda...")
                url = "https://api.github.com/repos/abzalbejokker11-afk/AyolimgaAgent/actions/workflows/post.yml/dispatches"
                GH_TOKEN = os.environ.get("GH_TOKEN", "")
                if GH_TOKEN:
                    headers = {
                        "Authorization": f"Bearer {GH_TOKEN}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                    data = {"ref": "main"}
                    r = requests.post(url, headers=headers, json=data)
                    print(f"Trigger natijasi: {r.status_code}")
                # Bir daqiqa kutamizki, yana qayta yubormasin
                time.sleep(65)
            else:
                time.sleep(30)
        except Exception as e:
            print("Scheduler xatosi:", e)
            time.sleep(60)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    t_sched = Thread(target=schedule_posts)
    t_sched.daemon = True
    t_sched.start()
