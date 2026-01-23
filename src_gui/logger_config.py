import logging
import os
from dotenv import load_dotenv

_ = load_dotenv()


handlers = [logging.StreamHandler()]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=handlers,
)
logger = logging.getLogger(__name__)