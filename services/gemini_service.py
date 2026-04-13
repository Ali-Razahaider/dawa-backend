from google import genai
from config import settings
from google.genai import types
import requests

client = genai.Client(api_key=settings.gemini_api_key)


async def generate_prescription(image_url: str):
    image_path = image_url
    image_bytes = requests.get(image_path).content
    image = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    prompt = ' Extract medication names and their dosages from the prescription image. Return the result in valid JSON format as: {"medications": [{"name": "Medication Name", "dosage": "Dosage"}]}. Only return JSON.'

    response = client.models.generate_content(
        model="gemini-3-flash-preview", contents=[prompt, image]
    )

    return response.text
