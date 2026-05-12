import requests

API_KEY = "AIzaSyADKqHQirxtbdWZthPf_utgI1oX-oIDkwA"

# List available models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
r = requests.get(url, timeout=10)
if r.status_code == 200:
    models = r.json().get("models", [])
    for m in models:
        name = m.get("name", "")
        if "flash" in name.lower() and "generateContent" in str(m.get("supportedGenerationMethods", [])):
            print(name)
else:
    print("Error:", r.text[:200])
