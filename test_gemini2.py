import requests
import time

API_KEY = "AIzaSyCHb0Fh6RUMLecbG25KxYOVkXFI7I6Qjk4"

# Try gemini-2.5-flash-preview instead
models = ["gemini-2.5-flash-preview-05-20", "gemini-2.0-flash-lite", "gemini-1.5-flash"]

for model in models:
    print(f"\nTrying {model}...")
    time.sleep(2)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "วิเคราะห์ราคาทองคำ XAUUSD ตอนนี้ $4,727 ให้สั้นๆ 2-3 ประโยค ภาษาไทย"}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 200}
    }
    r = requests.post(url, json=payload, timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"OK: {text}")
        break
    else:
        err = r.json().get("error", {}).get("message", "")[:100]
        print(f"Error: {err}")
