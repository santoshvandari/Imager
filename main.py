import os
import time
import random
import requests
import base64
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO

# Configuration
SEARCH_TERMS = ["cute kittens", "beautiful landscapes", "cyberpunk city"]
NUMBER_OF_IMAGES = 5
SAVE_FOLDER = "downloaded_images"
LOG_FILE = "scraper.log"

# GOOGLE IMAGE URL
GOOGLE_IMAGES_URL = "https://www.google.com/search?tbm=isch&q="

# Logger Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_driver():
    logger.info("Setting up Chrome driver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        """
    })
    logger.info("Driver setup complete.")
    return driver

def random_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0):
    sleep_time = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
    time.sleep(sleep_time)

def scroll_page(driver, scrolls=5):
    logger.info(f"Scrolling page {scrolls} times...")
    for i in range(scrolls):
        driver.execute_script("window.scrollBy(0, 1000);")
        random_sleep(1, 2)
    
    try:
        possible_selectors = [".mye4qd", ".LZ4I", "input[value='Show more results']"]
        for selector in possible_selectors:
            try:
                show_more_btn = driver.find_element(By.CSS_SELECTOR, selector)
                if show_more_btn.is_displayed():
                    logger.info("Clicking 'Show more results' button")
                    show_more_btn.click()
                    random_sleep(2, 3)
                    break
            except:
                continue
    except Exception as e:
        logger.debug(f"No 'Show more results' button found: {e}")

def download_image(url, folder_path, image_name):
    try:
        if url.startswith("data:image"):
            logger.debug(f"Downloading base64 image: {image_name}")
            header, encoded = url.split(",", 1)
            data = base64.b64decode(encoded)
            img = Image.open(BytesIO(data))
            img.save(os.path.join(folder_path, f"{image_name}.jpg"), "JPEG")
            return True
        else:
            logger.debug(f"Downloading HTTP image: {image_name}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.save(os.path.join(folder_path, f"{image_name}.jpg"), "JPEG")
                return True
            else:
                logger.warning(f"Failed to download {image_name}: Status {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"Failed to download {image_name}: {e}")
        return False

def scrape_images(driver, query, num_images):
    logger.info(f"Starting scrape for: {query}")
    
    search_url = GOOGLE_IMAGES_URL + query.replace(" ", "+")
    driver.get(search_url)
    random_sleep(2, 3)
    
    main_window = driver.current_window_handle
    
    image_count = 0
    downloaded_urls = set()
    scroll_count = 0
    processed_indices = set()
    
    query_folder = os.path.join(SAVE_FOLDER, query.replace(" ", "_"))
    if not os.path.exists(query_folder):
        os.makedirs(query_folder)
        logger.info(f"Created directory: {query_folder}")
    
    while image_count < num_images and scroll_count < 20:  
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.Q4LuWd, img.rg_i, img.YQ4gaf"))
            )
        except Exception as e:
            logger.error(f"Timeout waiting for images: {e}")
            break
        
        thumbnail_selectors = ["img.YQ4gaf", "img.Q4LuWd", "img.rg_i"]
        
        thumbnails = []
        active_selector = None
        
        for selector in thumbnail_selectors:
            thumbnails = driver.find_elements(By.CSS_SELECTOR, selector)
            if thumbnails:
                active_selector = selector
                logger.info(f"Found {len(thumbnails)} thumbnails with selector: {selector}")
                break
        
        if not thumbnails:
            logger.warning("No thumbnails found, scrolling...")
            scroll_page(driver, 3)
            scroll_count += 1
            random_sleep(1, 2)
            continue
        
        images_downloaded_this_round = 0
        
        for idx in range(len(thumbnails)):
            if image_count >= num_images:
                break
            
            if idx in processed_indices:
                continue
            
            try:
                current_thumbnails = driver.find_elements(By.CSS_SELECTOR, active_selector)
                if idx >= len(current_thumbnails):
                    continue
                
                thumbnail = current_thumbnails[idx]
                
                if not thumbnail.is_displayed():
                    processed_indices.add(idx)
                    continue
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thumbnail)
                random_sleep(0.3, 0.6)
                
                driver.execute_script("arguments[0].click();", thumbnail)
                random_sleep(1, 1.5)
                
                current_windows = driver.window_handles
                if len(current_windows) > 1:
                    for window in current_windows:
                        if window != main_window:
                            driver.switch_to.window(window)
                            driver.close()
                            logger.debug(f"Closed extra tab/window")
                    driver.switch_to.window(main_window)
                
                img_selectors = [
                    "img.sFlh5c.pT0Scc.iPVvYb",  # Google Images specific
                    "img.n3VNCb",                 # Alternative Google selector
                    "img.iPVvYb",                 # Simplified selector
                    "img[jsname='kn3ccd']",       # Another Google selector
                    "img[jsname='HiaYvf']",       # Yet another variant
                    "div[data-id] img",           # Images inside preview divs
                    "a[jsname='sTFXNd'] img",     # Images in preview links
                ]
                
                found_image = False
                
                # First try specific selectors
                for img_selector in img_selectors:
                    try:
                        actual_images = driver.find_elements(By.CSS_SELECTOR, img_selector)
                        
                        for actual_image in actual_images:
                            src = actual_image.get_attribute('src') or actual_image.get_attribute('data-src')
                            
                            if not src or src in downloaded_urls:
                                continue
                            
                            if 'data:image/gif' in src or 'data:image/svg' in src or len(src) < 100:
                                continue
                            
                            try:
                                width = actual_image.get_attribute('naturalWidth') or actual_image.get_attribute('width')
                                height = actual_image.get_attribute('naturalHeight') or actual_image.get_attribute('height')
                                if width and height:
                                    if int(width) < 100 or int(height) < 100:
                                        continue
                            except:
                                pass  # If we can't get dimensions, try downloading anyway
                            
                            if "http" in src or "data:image/jpeg" in src or "data:image/png" in src:
                                if download_image(src, query_folder, f"img_{image_count}"):
                                    downloaded_urls.add(src)
                                    image_count += 1
                                    images_downloaded_this_round += 1
                                    processed_indices.add(idx)
                                    logger.info(f"Downloaded {image_count}/{num_images} for '{query}' using selector: {img_selector}")
                                    found_image = True
                                    break
                        
                        if found_image:
                            break
                    except Exception as e:
                        logger.debug(f"Selector {img_selector} failed: {str(e)[:50]}")
                        continue
                
                if not found_image:
                    try:
                        logger.debug(f"Trying generic img search for thumbnail {idx}")
                        all_images = driver.find_elements(By.TAG_NAME, "img")
                        
                        # Sort by size to get the largest images first
                        valid_images = []
                        for img in all_images:
                            try:
                                src = img.get_attribute('src') or img.get_attribute('data-src')
                                if not src or src in downloaded_urls:
                                    continue
                                
                                if 'data:image/gif' in src or 'data:image/svg' in src or len(src) < 100:
                                    continue
                                
                                # Try to get image size
                                width = img.get_attribute('naturalWidth') or img.get_attribute('width') or 0
                                height = img.get_attribute('naturalHeight') or img.get_attribute('height') or 0
                                
                                try:
                                    width = int(width)
                                    height = int(height)
                                except:
                                    width = 0
                                    height = 0
                                
                                if width >= 200 and height >= 200:
                                    valid_images.append((img, src, width * height))
                            except:
                                continue
                        
                        # Sort by size (largest first)
                        valid_images.sort(key=lambda x: x[2], reverse=True)
                        
                        # Try to download the largest valid image
                        for img, src, size in valid_images[:3]:  # Try top 3 largest
                            if "http" in src or "data:image/jpeg" in src or "data:image/png" in src:
                                if download_image(src, query_folder, f"img_{image_count}"):
                                    downloaded_urls.add(src)
                                    image_count += 1
                                    images_downloaded_this_round += 1
                                    processed_indices.add(idx)
                                    logger.info(f"Downloaded {image_count}/{num_images} for '{query}' using generic search")
                                    found_image = True
                                    break
                    except Exception as e:
                        logger.debug(f"Generic img search failed: {str(e)[:50]}")
                
                if not found_image:
                    processed_indices.add(idx)  # Mark as processed even if failed
                    
            except Exception as e:
                logger.debug(f"Error processing thumbnail {idx}: {str(e)[:50]}")
                processed_indices.add(idx)  # Mark as processed to avoid retrying
                continue
        
        if images_downloaded_this_round == 0:
            logger.info(f"No new images found. Scrolling for more content...")
            scroll_page(driver, 3)
            scroll_count += 1
            random_sleep(1, 2)
    
    logger.info(f"Finished downloading {image_count} images for: {query}")

def main():
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)
    
    driver = None
    try:
        driver = setup_driver()
        for term in SEARCH_TERMS:
            scrape_images(driver, term, NUMBER_OF_IMAGES)
    except Exception as e:
        logger.critical(f"Critical error in main execution: {e}", exc_info=True)
    finally:
        if driver:
            logger.info("Closing driver...")
            driver.quit()

if __name__ == "__main__":
    main()