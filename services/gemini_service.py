from google import genai
from config import settings
from google.genai import types
import json
from schemas import ExtractedMedicines, MedicineItem

client = genai.Client(api_key=settings.gemini_api_key)


async def generate_prescription(image_bytes: bytes) -> ExtractedMedicines:
    image = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    prompt = "Analyze the prescription image and extract all medicines."

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedMedicines,
            ),
        )

        if not response.text:
            return ExtractedMedicines(medicines=[])

        data = json.loads(response.text)
        
        # Validation and conversion
        if isinstance(data, dict) and "medicines" in data:
            medicines_data = data["medicines"]
        elif isinstance(data, list):
            medicines_data = data
        else:
            medicines_data = []

        medicines = []
        for m in medicines_data:
            if not m.get("name"): continue
            medicines.append(MedicineItem(**m))
        
        return ExtractedMedicines(medicines=medicines)

    except Exception as e:
        print(f"Error in Gemini: {e}")
        return ExtractedMedicines(medicines=[])
