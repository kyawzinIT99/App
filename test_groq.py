import os
import requests

# Read API key from environment variable (simulate Streamlit secret)
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    print("❌ API key not found in environment")
else:
    print("✅ API key found")

    # Optional: make a test call to Groq API
    url = "https://api.groq.com/llm"  # adjust if needed
    payload = {"prompt": "Say hello", "model": "groq-1"}
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=5)
        if r.ok:
            print("✅ Groq API request successful!")
            print("Response:", r.json())
        else:
            print("❌ Groq API request failed. Status:", r.status_code, r.text)
    except Exception as e:
        print("❌ Groq API request error:", e)
