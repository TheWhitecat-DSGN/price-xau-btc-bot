import requests

API_KEY = "AIzaSyADKqHQirxtbdWZthPf_utgI1oX-oIDkWA"

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
    print("Error:", r.text[:200])
