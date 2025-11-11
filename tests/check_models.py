import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("Available Gemini models:")
try:
    models = genai.list_models()
    for model in models:
        if 'gemini' in model.name.lower():
            print(f"  - {model.name} (supports generate_content: {model.supported_generation_methods})")
except Exception as e:
    print(f"Error: {e}")
