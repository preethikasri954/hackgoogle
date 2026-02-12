import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

print(f"Testing API Key: {api_key[:5]}...{api_key[-5:]}")

try:
    genai.configure(api_key=api_key)
    # List models to see if we have access
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
            
    model = genai.GenerativeModel('gemini-1.5-flash') # Try a newer model just in case
    print("Generating content...")
    response = model.generate_content("Hello")
    print("Success: Gemini API responded.")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: Failed to connect to Gemini API.")
    traceback.print_exc()
    exit(1)
