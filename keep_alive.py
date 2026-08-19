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
    try:
        async def run_tts():
            comm = edge_tts.Communicate("Salom", "uz-UZ-MadinaNeural")
            await comm.save("test.mp3")
        asyncio.run(run_tts())
        return "TTS Success!"
    except Exception as e:
        return f"TTS Failed: {e}"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
