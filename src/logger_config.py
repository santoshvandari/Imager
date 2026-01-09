import logging
import os
from dotenv import load_dotenv

_ = load_dotenv()


LOG_FILE = os.getenv("LOG_FILE", "scraper.log")
# Logger Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)