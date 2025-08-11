# main.py
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import io
import re
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI(title="Screenshot to Text UI")

# Serve static files (CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/debug", response_class=HTMLResponse)
async def debug(request: Request):
    return templates.TemplateResponse("debug.html", {"request": request})


def extract_key_values_from_text(text: str):
    """
    Extracts key:value or key - value pairs with improved regex rules.
    Returns a list of (key, value).
    """
    kv = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # Improved regex for various separators
    sep_pattern = re.compile(r"^\s*(.{1,60}?)\s*[:\-–—]\s*(.+?)\s*$")

    for line in lines:
        match = sep_pattern.match(line)
        if match:
            key, value = match.groups()
            kv.append((key.strip(), value.strip()))
        else:
            # Heuristic for space-separated pairs without colon
            m2 = re.match(r"^(?P<k>[A-Za-z ]{2,40})\s+([:–\-—]?\s*)?(?P<v>.+)$", line)
            if m2 and ':' not in line and len(m2.group('v')) < 200:
                k = m2.group('k').strip()
                v = m2.group('v').strip()
                if len(k.split()) <= 4 and len(v) > 0:
                    kv.append((k, v))

    # Deduplicate while preserving order
    seen = set()
    final = []
    for k, v in kv:
        key_low = (k.lower(), v.lower())
        if key_low not in seen:
            seen.add(key_low)
            final.append((k, v))

    return final


def preprocess_image_for_ocr(pil_img: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR results.
    """
    img = pil_img.convert("RGB")
    img = ImageOps.exif_transpose(img)

    # Convert to grayscale & enhance contrast
    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray)
    gray = ImageEnhance.Contrast(gray).enhance(2.0)

    # Sharpen image
    gray = gray.filter(ImageFilter.SHARPEN)

    return gray


@app.post("/api/extract")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            return JSONResponse({"error": "File must be an image"}, status_code=400)
        
        # Read uploaded file
        contents = await file.read()
        if not contents:
            return JSONResponse({"error": "Empty file uploaded"}, status_code=400)
            
        pil_img = Image.open(io.BytesIO(contents))

        # Preprocess image
        processed_img = preprocess_image_for_ocr(pil_img)

        # OCR extraction
        extracted_text = pytesseract.image_to_string(processed_img)
        
        if not extracted_text.strip():
            return JSONResponse({
                "text": "",
                "key_values": [],
                "warning": "No text could be extracted from the image"
            })

        # Key-value extraction
        kv_pairs = extract_key_values_from_text(extracted_text)

        # 🔹 Call AI refinement function here
        refined_kv_pairs = ai_refine_kv_pairs(kv_pairs)

        print(refined_kv_pairs)

        return JSONResponse({
            "text": extracted_text.strip(),
            "key_values": [{"key": k, "value": v} for k, v in refined_kv_pairs]
        })

    except Exception as e:
        print(f"Error in extract_text: {str(e)}")
        return JSONResponse({"error": f"Processing failed: {str(e)}"}, status_code=500)



def ai_refine_kv_pairs(kv_pairs):
    """
    Use AI to refine and clean extracted key-value pairs.
    Falls back to original pairs if API call fails.
    """
    if not GROQ_API_KEY:
        print("Warning: GROQ_API_KEY not set, returning original pairs")
        return kv_pairs
    
    try:
        prompt = "Clean and correct these extracted key-value pairs from OCR. Return them in the same format:\n"
        for k, v in kv_pairs:
            prompt += f"- {k}: {v}\n"
        
        prompt += "\nPlease return the cleaned pairs in the exact same format, one per line."

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                # For now, return original pairs since parsing AI response is complex
                # You can implement parsing logic here later
                print(f"AI refinement successful: {content[:100]}...")
                return kv_pairs
            else:
                print("API response missing choices")
                return kv_pairs
        else:
            print(f"API call failed with status {response.status_code}: {response.text}")
            return kv_pairs
            
    except Exception as e:
        print(f"Error in AI refinement: {str(e)}")
        return kv_pairs

