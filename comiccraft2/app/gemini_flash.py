import json, os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")

FALLBACK = {
    "panels": [
        {"panel": 1, "title": "The Unexpected Bell", "scene": "Ari arrives at Dragon School and a mysterious bell rings before class begins."},
        {"panel": 2, "title": "The Smallest Dragon", "scene": "Ari meets a tiny dragon hiding behind a stack of books."},
        {"panel": 3, "title": "The Teamwork Test", "scene": "Ari and the tiny dragon must work together during a funny flying lesson."},
        {"panel": 4, "title": "A Different Kind of Fire", "scene": "The dragon discovers a surprising special power that helps save the class project."},
        {"panel": 5, "title": "The Dragon School Promise", "scene": "Ari and the dragon become friends and promise to face every new adventure together."},
    ]
}

def generate_outline(prompt, character, setting, tone, art_style):
    key = os.getenv("GEMINI_API_KEY")
    if not key or key.startswith("PASTE_"):
        return FALLBACK
    try:
        client = genai.Client(api_key=key)
        schema = {"type": "OBJECT", "properties": {"panels": {"type": "ARRAY", "minItems": 5, "maxItems": 5, "items": {"type": "OBJECT", "properties": {"panel": {"type": "INTEGER"}, "title": {"type": "STRING"}, "scene": {"type": "STRING"}}, "required": ["panel", "title", "scene"]}}}, "required": ["panels"]}
        response = client.models.generate_content(
            model=MODEL,
            contents=f"Create exactly 5 comic panels. Story: {prompt}. Character: {character}. Setting: {setting}. Tone: {tone}. Art style: {art_style}. Keep it student-friendly, funny/adventurous and easy to illustrate.",
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema, temperature=0.8),
        )
        return json.loads(response.text)
    except Exception:
        return FALLBACK
