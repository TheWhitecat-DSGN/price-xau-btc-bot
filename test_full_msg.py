import requests
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyADKqHQirxtbdWZthPf_utgI1oX-oIDkwA"
TOKEN = "8511076929:AAFMJUMc1m4O2xylOa1H6RJeGkvt8M-x6s8"
CHAT_ID = "1027083696"

# Get prices
gold_r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/GC=F?range=1d&interval=1m", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
g = gold_r.json()["chart"]["result"][0]["meta"]
gold_price = g["regularMarketPrice"]
gold_prev = g["chartPreviousClose"]
gold_change = gold_price - gold_prev
gold_pct = (gold_change / gold_prev) * 100

btc_r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true", timeout=10)
btc = btc_r.json()["bitcoin"]

g_emoji = "🟢" if gold_change >= 0 else "🔴"
b_emoji = "🟢" if btc["usd_24h_change"] >= 0 else "🔴"

# Gemini analysis
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
prompt = f"""You are a market analyst. Write a short Thai language analysis.
Gold (XAUUSD): ${gold_price:,.2f} ({gold_pct:+.2f}%)
Bitcoin: ${btc['usd']:,.2f} ({btc['usd_24h_change']:+.2f}%)
Provide in Thai:
1. สรุปตลาดวันนี้ (1-2 ประโยค)
2. จุดสำคัญที่ต้องจับตา
3. แนวโน้มระยะสั้น
Keep under 300 chars. Use emoji."""

payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 300}}
r = requests.post(url, json=payload, timeout=30)
analysis = ""
if r.status_code == 200:
    analysis = r.json()["candidates"][0]["content"]["parts"][0]["text"]

msg = f"""📊 ราคาตลาดวันนี้
📅 12/05/2026
━━━━━━━━━━━━━━━━━━

🥇 ทองคำ (XAUUSD)
   ${gold_price:,.2f} / oz
   {g_emoji} {gold_change:+,.2f} ({gold_pct:+,.2f}%)

🟠 Bitcoin (BTCUSD)
   ${btc['usd']:,.2f}
   {b_emoji} {btc['usd_24h_change']:+.2f}% (24h)

━━━━━━━━━━━━━━━━━━

🔬 วิเคราะห์
{analysis}

💡 /gold /btc /all /analyze"""

r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg})
print("Sent:", r.json().get("ok"))
