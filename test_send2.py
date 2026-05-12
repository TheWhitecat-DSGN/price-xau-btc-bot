import requests
import os

token = "8511076929:AAFMJUMc1m4O2xylOa1H6RJeGkvt8M-x6s8"
chat_id = "1027083696"

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

msg = f"""📊 ราคาตลาดวันนี้
📅 12/05/2026 12:15 น.
━━━━━━━━━━━━━━━━━━

🥇 ทองคำ (XAUUSD)
   ${gold_price:,.2f} / oz
   {g_emoji} {gold_change:+,.2f} ({gold_pct:+,.2f}%)

🟠 Bitcoin (BTCUSD)
   ${btc["usd"]:,.2f}
   {b_emoji} {btc["usd_24h_change"]:+.2f}% (24h)

━━━━━━━━━━━━━━━━━━

🔬 วิเคราะห์จะเปิดใช้งานเมื่อตั้ง GEMINI_API_KEY

💡 /gold /btc /all /analyze"""

r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg})
print("OK:", r.json().get("ok"))
