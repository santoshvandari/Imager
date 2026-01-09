import json
import random
from logger_config import logger
import time
from io import BytesIO
import base64
from PIL import Image
import requests
import os
from typing import cast


def _load_user_agents() -> list[dict[str, str]]:
    """Loads user agents from user_agent.json."""
    file_path = os.path.join(os.path.dirname(__file__), "user_agent.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return cast(list[dict[str, str]], json.load(f))
        logger.error(f"user_agent.json not found at {file_path}")
    except Exception as e:
        logger.error(f"Failed to load user agents: {e}")
    return []


USER_AGENTS_LIST: list[dict[str, str]] = _load_user_agents()


def random_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    sleep_time = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
    time.sleep(sleep_time)


def get_user_agent() -> str:
    """
    Function to get a random user agent
    Returns:
        str: A random user agent
    """
    if not USER_AGENTS_LIST:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    user_agent_dict = random.choice(USER_AGENTS_LIST)
    return (
        user_agent_dict.get("useragent")
        or user_agent_dict.get("user_agent")
        or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )


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
            headers = {"User-Agent": get_user_agent()}
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
