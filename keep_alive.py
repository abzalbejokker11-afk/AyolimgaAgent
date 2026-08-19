import os
from flask import Flask
from threading import Thread

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

def keep_alive():
    t = Thread(target=run)
    t.start()
