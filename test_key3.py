import requests

API_KEY = "AIzaSyDnROLGlUyAnUsuvc9JLUaHUPsjNaw_7Zg"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
payload = {
    "contents": [{"parts": [{"text": "วิเคราะห์ราคาทองคำ XAUUSD ตอนนี้ $4,727 ให้สั้นๆ 2-3 ประโยค ภาษาไทย"}]}],
    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 200}
}
r = requests.post(url, json=payload, timeout=30)
print("Status:", r.status_code)
if r.status_code == 200:
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    print("OK:", text)
else:
    print("Error:", r.text[:200])
