from google import genai
from config import settings
from google.genai import types
import requests
import json

client = genai.Client(api_key=settings.gemini_api_key)


async def generate_prescription(image_url: str):
    image_path = image_url
    image_bytes = requests.get(image_path).content
    image = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    prompt = """
You are a medical assistant specialized in reading handwritten prescriptions.

Analyze the prescription image and extract all medicines the doctor has written.

Rules:
- Extract only medicines, ignore doctor name, patient name, date, and signatures
- If the handwriting is unclear, make your best guess based on medical knowledge
- If no medicines are found, return an empty list
- Do NOT include any explanation, markdown, or extra text — only raw JSON

Return exactly this format:
{
    "medicines": [
        {
            "name": "medicine name as written",
            "dosage": "dose amount e.g. 500mg",
            "frequency": "how many times a day e.g. 1+0+1",
            "duration": "how many days e.g. 7 days"
        }
    ]
}
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview", contents=[prompt, image]
    )

    return json.loads(response.text or "")
