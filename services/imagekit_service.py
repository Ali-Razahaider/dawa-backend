from fastapi import HTTPException
from images import imagekit


async def upload_file(
    file_bytes: bytes,
    file_name: str,
) -> str:
    try:
        response = imagekit.files.upload(
            file=file_bytes,
            file_name=file_name,
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Image upload service is unavailable right now.",
        )

    file_url = response.url or ""

    if not file_url:
        raise HTTPException(
            status_code=502,
            detail="Image upload failed. Please try again.",
        )

    return file_url
