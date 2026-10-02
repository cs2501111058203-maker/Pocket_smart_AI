import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from google import genai
from PIL import Image
import io

load_dotenv()

app = FastAPI(title="PocketSmart-AI")
templates = Jinja2Templates(directory="templates")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.8-flash"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request, "result": None})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, file: UploadFile = File(None), text_input: str = Form("")):
    try:
        if not text_input and (not file or not file.filename):
            result = "⚠️ Please type your expense like 'I spent 500 on Swiggy'"
        else:
            prompt = f"""
            You are PocketSmart AI for Indian students.
            Expense: {text_input}
            Give: 1) Category 2) Necessary or waste? 3) Saving tip 4) Budget advice
            Short, friendly, in Rupees.
            """
            contents = [prompt]
            if file and file.filename:
                img = Image.open(io.BytesIO(await file.read()))
                contents.append(img)

            # Retry 3 times if Google is busy (503 error)
            result = ""
            for i in range(3):
                try:
                    response = client.models.generate_content(model=MODEL_NAME, contents=contents)
                    result = response.text
                    break
                except Exception as e:
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        time.sleep(2) # wait 2 sec and try again
                        result = f"Google busy, retrying... ({i+1}/3)"
                        continue
                    else:
                        raise e
            if not result or "retrying" in result:
                result = "Google AI is busy due to high demand. Please click Analyze again in 10 seconds!"

    except Exception as e:
        result = f"Error: {e}"

    return templates.TemplateResponse(request, "index.html", {"request": request, "result": result})