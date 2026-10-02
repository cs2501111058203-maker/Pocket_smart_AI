import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print("Key loaded:", str(key)[:15] + "...")

client = genai.Client(api_key=key)
response = client.models.generate_content(
        model='gemini-3.8-flash',
    contents='Say Hi PocketSmart AI is working in 1 line!'
)
print(response.text)
print("SUCCESS - Your Gemini is working!")