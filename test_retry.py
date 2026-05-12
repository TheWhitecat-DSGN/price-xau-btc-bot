import requests
import time

API_KEY = "AIzaSyDnROLGlUyAnUsuvc9JLUaHUPsjNaw_7Zg"

# Wait a moment then try
time.sleep(3)
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
payload = {
    "contents": [{"parts": [{"text": "Say hello in Thai, one sentence only."}]}],
    "generationConfig": {"maxOutputTokens": 50}
}
r = requests.post(url, json=payload, timeout=30)
print("Status:", r.status_code)
if r.status_code == 200:
    print("OK:", r.json()["candidates"][0]["content"]["parts"][0]["text"])
else:
    err = r.json().get("error", {})
    print("Code:", err.get("code"))
    print("Msg:", err.get("message", "")[:200])
