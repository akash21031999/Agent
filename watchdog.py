# watchdog.py
import os
from google import genai

# Setup
TICKERS = ["ASML", "VRT", "KLAC", "ASX"]
API_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELE_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELE_ID")

def send_alert(message):
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def run_check():
    client = genai.Client(api_key=API_KEY)
    for ticker in TICKERS:
        # AI checks for news & asymmetry score
        prompt = f"Check latest news for {ticker}. Has the 'Asymmetry Score' changed? Reply with ONLY 'YES' or 'NO'."
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        
        if "YES" in response.text.upper():
            send_alert(f"🚀 ALPHA ALERT: Asymmetry score changed for ${ticker}. Check your dashboard!")

if __name__ == "__main__":
    run_check()
