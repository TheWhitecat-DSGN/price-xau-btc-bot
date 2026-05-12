import requests

token = "8511076929:AAFMJUMc1m4O2xylOa1H6RJeGkvt8M-x6s8"
chat_id = "1027083696"

msg = """📊 ราคาทองคำ + BTC
━━━━━━━━━━━━━━━━━━

🥇 ทองคำ (XAUUSD)
   $4,720.70 / oz
   🔴 -8.00 (-0.17%)

🟠 Bitcoin (BTCUSD)
   $81,218.00
   🟢 +0.48% (24h)

━━━━━━━━━━━━━━━━━━
💡 พิมพ์ /gold /btc /all"""

r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": msg})
print("Status:", r.status_code)
print("Response:", r.text)
