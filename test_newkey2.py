import requests

API_KEY = "AIzaSyADKqHQirxtbdWZthPf_utgI1oX-oIDkwA"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
payload = {
    "contents": [{"parts": [{"text": "วิเคราะห์ราคาทองคำ XAUUSD ตอนนี้ $4,727 ให้สั้นๆ 2-3 ประโยค ภาษาไทย"}]}],
    "generationConfig": {"maxOutputTokens": 200}
}
r = requests.post(url, json=payload, timeout=30)
print("Status:", r.status_code)
if r.status_code == 200:
    print("OK:", r.json()["candidates"][0]["content"]["parts"][0]["text"])
else:
    print("Error:", r.text[:200])
