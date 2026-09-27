import json, os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")

def generate_story(outline, character, tone):
    fallback = []
    for p in outline["panels"]:
        fallback.append({"panel": p["panel"], "caption": p["title"], "narration": p["scene"], "dialogue": f'{character}: "This is going to be an amazing adventure!"'})
    key = os.getenv("GEMINI_API_KEY")
    if not key or key.startswith("PASTE_"):
        return {"panels": fallback}
    try:
        client = genai.Client(api_key=key)
        schema = {"type":"OBJECT","properties":{"panels":{"type":"ARRAY","minItems":5,"maxItems":5,"items":{"type":"OBJECT","properties":{"panel":{"type":"INTEGER"},"caption":{"type":"STRING"},"narration":{"type":"STRING"},"dialogue":{"type":"STRING"}},"required":["panel","caption","narration","dialogue"]}}},"required":["panels"]}
        response = client.models.generate_content(model=MODEL, contents=f"Turn this 5-panel outline into detailed but concise comic narration and dialogue. Main character: {character}. Tone: {tone}. Outline: {json.dumps(outline)}", config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema, temperature=0.8))
        return json.loads(response.text)
    except Exception:
        return {"panels": fallback}
