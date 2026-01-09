import os

from .logger_config import logger
from dotenv import load_dotenv
_ = load_dotenv()

# Modular Import
from .setup_driver import setup_driver
from .scrape_image import scrape_images

# Configuration
SEARCH_TERMS_RAW = os.getenv("SEARCH_TERMS", None)
if not SEARCH_TERMS_RAW:
    raise ValueError("SEARCH_TERMS is not set in the environment variables")
SEARCH_TERMS = SEARCH_TERMS_RAW.split(",")
NUMBER_OF_IMAGES = int(os.getenv("NUMBER_OF_IMAGES", 5))
SAVE_FOLDER = os.getenv("SAVE_FOLDER", "downloaded_images")

def main():
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    driver = None
    try:
        driver = setup_driver()
        for term in SEARCH_TERMS:
            scrape_images(driver, term, NUMBER_OF_IMAGES)
    except Exception as e:
        logger.error(f"Critical error in main execution: {e}", exc_info=True)
    finally:
        if driver:
            logger.info("Closing driver...")
            driver.quit()


if __name__ == "__main__":
    main()
