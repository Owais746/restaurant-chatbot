import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Test OpenRouter API connection
api_key = os.getenv('OPENROUTER_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key found")

headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "http://localhost:8501",
    "X-Title": "Restaurant Chatbot Test"
}

data = {
    "model": "tngtech/deepseek-r1t2-chimera:free",
    "messages": [
        {
            "role": "user",
            "content": "Hello, can you help me with a pizza order?"
        }
    ]
}

try:
    print("Making API request...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print("API Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error Response: {response.text}")
        
except Exception as e:
    print(f"Exception occurred: {e}")
