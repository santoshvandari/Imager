import logging
import os
from dotenv import load_dotenv

load_dotenv()


LOG_FILE = os.getenv("LOG_FILE", "scraper.log")
DISABLE_LOG_FILE = os.getenv("DISABLE_LOG_FILE", "False").lower() == "true"

handlers = [logging.StreamHandler()]
if not DISABLE_LOG_FILE:
    handlers.append(logging.FileHandler(LOG_FILE))

# Logger Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=handlers,
)
logger = logging.getLogger(__name__)