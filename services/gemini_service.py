from google import genai
from config import settings
from google.genai import types
import json
from schemas import ExtractedMedicines, MedicineItem

client = genai.Client(api_key=settings.gemini_api_key)


async def generate_prescription(image_bytes: bytes) -> ExtractedMedicines:
    image = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    prompt = """
Analyze the prescription image and extract all medicines.
Extract only medicines. If handwriting is unclear, make your best guess based on medical context.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractedMedicines,
        ),
    )

    if not response.text:
        return ExtractedMedicines(medicines=[])

    try:
        data = json.loads(response.text)
        return ExtractedMedicines(**data)
    except Exception:
        # Fallback if structure is slightly different
        raw_response = json.loads(response.text)
        medicines_data = raw_response.get("medicines", [])
        medicines = [MedicineItem(**m) for m in medicines_data]
        return ExtractedMedicines(medicines=medicines)
