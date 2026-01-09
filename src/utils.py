import random
from .logger_config import logger
import time
from io import BytesIO
import base64
from PIL import Image
import requests
import os


def random_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    sleep_time = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
    time.sleep(sleep_time)


def download_image(url: str, folder_path: str, image_name: str) -> bool:
    try:
        if url.startswith("data:image"):
            logger.debug(f"Downloading base64 image: {image_name}")
            _, encoded = url.split(",", 1)
            data = base64.b64decode(encoded)
            img = Image.open(BytesIO(data))
            img.save(os.path.join(folder_path, f"{image_name}.jpg"), "JPEG")
            return True
        else:
            logger.debug(f"Downloading HTTP image: {image_name}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.save(os.path.join(folder_path, f"{image_name}.jpg"), "JPEG")
                return True
            else:
                logger.warning(
                    f"Failed to download {image_name}: Status {response.status_code}"
                )
                return False
    except Exception as e:
        logger.error(f"Failed to download {image_name}: {e}")
        return False
