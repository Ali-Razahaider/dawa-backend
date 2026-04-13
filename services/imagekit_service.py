import logging
from images import imagekit


logger = logging.getLogger(__name__)


async def upload_file(
    file_bytes: bytes,
    file_name: str,
    folder: str = "/prescriptions",
) -> str:
    response = imagekit.files.upload(
        file=file_bytes,
        file_name=file_name,
    )

    file_url = response.url or ""
    logger.info(f"Uploaded {file_name}: {file_url}")

    return file_url
