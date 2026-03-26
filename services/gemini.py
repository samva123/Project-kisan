import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#MODEL = "gemini-3-flash-preview"  # Free experimental model, no billing needed
MODEL = "gemini-3.1-flash-lite-preview"

def _generate_with_retry(contents, retries=3, wait=60):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents
            )
            return response.text
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                if attempt < retries - 1:
                    print(f"Rate limited. Waiting {wait}s... (attempt {attempt+2}/{retries})")
                    time.sleep(wait)
                else:
                    raise Exception("Quota exceeded. Wait a minute and try again.")
            else:
                raise e


async def diagnose_crop(image_bytes: bytes, mime_type: str, language: str = "English") -> str:
    prompt = f"""
    You are an expert agronomist helping a small farmer in India.
    Analyze this crop image carefully and respond in {language}.

    Provide:
    1. **Disease/Problem Name** - What is affecting the crop?
    2. **Confidence** - How sure are you? (High/Medium/Low)
    3. **Symptoms** - What symptoms do you see in the image?
    4. **Cause** - What causes this?
    5. **Immediate Action** - What should the farmer do RIGHT NOW?
    6. **Treatment** - Specific, locally available and affordable remedies
    7. **Prevention** - How to avoid this in future?

    Be practical. Recommend cheap, locally available solutions.
    Avoid technical jargon. Speak like you're talking to a farmer.
    """
    contents = [
        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        types.Part.from_text(text=prompt),
    ]
    return _generate_with_retry(contents)


async def analyze_market(crop_name: str, market_data: dict, language: str = "English") -> str:
    prompt = f"""
    You are a market analyst helping a small farmer in India.
    Respond in {language}.

    Crop: {crop_name}
    Market Data: {market_data}

    Provide:
    1. **Current Price Range** - Min, Max, Modal price in simple terms
    2. **Best Market** - Which mandi has the best price today?
    3. **Trend** - Is price going up or down?
    4. **Recommendation** - Should the farmer sell today or wait?

    Keep it short, practical, and in simple language a farmer can understand.
    """
    return _generate_with_retry([types.Part.from_text(text=prompt)])


async def general_query(question: str, language: str = "English") -> str:
    prompt = f"""
    You are a helpful agricultural assistant for farmers in India.
    Answer in {language}. Keep answers practical and simple.

    Question: {question}

    If asked about government schemes, mention eligibility, benefits, and how to apply.
    If asked about farming tips, give actionable advice.
    Always be concise and farmer-friendly.
    """
    return _generate_with_retry([types.Part.from_text(text=prompt)])