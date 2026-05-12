import requests

API_KEY = "AIzaSyADKqHQirxtbdWZthPf_utgI1oX-oIDkwA"

models = ["gemini-2.5-flash-preview-05-20", "gemini-2.0-flash-001", "gemini-1.5-flash-002"]

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "วิเคราะห์ราคาทองคำ XAUUSD ตอนนี้ $4,727 ให้สั้นๆ 2-3 ประโยค ภาษาไทย"}]}],
        "generationConfig": {"maxOutputTokens": 200}
    }
    r = requests.post(url, json=payload, timeout=30)
    print(f"{m}: {r.status_code}")
    if r.status_code == 200:
        print(r.json()["candidates"][0]["content"]["parts"][0]["text"])
        break
    else:
        print(r.text[:150])
