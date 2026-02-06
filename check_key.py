import google.generativeai as genai
import os

# PASTE YOUR API KEY DIRECTLY HERE FOR THIS TEST ONLY
MY_KEY = "AIzaSyC7JAQoT4jt64YmM_U50vTANm5lbmU2ZS0"

genai.configure(api_key=MY_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
