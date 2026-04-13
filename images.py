from imagekitio import ImageKit
from config import settings

imagekit = ImageKit(
    private_key=settings.imagekit_private_key,
)
