from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger_config import logger
from utils import random_sleep, download_image
import os
from dotenv import load_dotenv

_ = load_dotenv()

GOOGLE_IMAGES_URL = os.getenv(
    "GOOGLE_IMAGES_URL", "https://www.google.com/search?tbm=isch&q="
)
SAVE_FOLDER = os.getenv("SAVE_FOLDER", "downloaded_images")


def scroll_page(driver: webdriver.Chrome, scrolls: int = 5):
    logger.info(f"Scrolling page {scrolls} times...")
    for _ in range(scrolls):

        driver.execute_script(  # pyright: ignore[reportUnknownMemberType]
            "window.scrollBy(0, 1000);"
        )
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


def scrape_images(driver: webdriver.Chrome, query: str, num_images: int):
    logger.info(f"Starting scrape for: {query}")

    search_url = GOOGLE_IMAGES_URL + query.replace(" ", "+")
    driver.get(search_url)
    random_sleep(2, 3)

    main_window = driver.current_window_handle

    image_count = 0
    downloaded_urls: set[str] = set()
    scroll_count = 0
    processed_indices: set[int] = set()

    query_folder = os.path.join(SAVE_FOLDER, query.replace(" ", "_"))
    if not os.path.exists(query_folder):
        os.makedirs(query_folder)
        logger.info(f"Created directory: {query_folder}")

    while image_count < num_images and scroll_count < 20:
        try:
            _ = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "img.Q4LuWd, img.rg_i, img.YQ4gaf")
                )
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
                logger.info(
                    f"Found {len(thumbnails)} thumbnails with selector: {selector}"
                )
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
                current_thumbnails = driver.find_elements(
                    By.CSS_SELECTOR, active_selector
                )
                if idx >= len(current_thumbnails):
                    continue

                thumbnail = current_thumbnails[idx]

                if not thumbnail.is_displayed():
                    processed_indices.add(idx)
                    continue

                driver.execute_script(  # pyright: ignore[reportUnknownMemberType]
                    "arguments[0].scrollIntoView({block: 'center'});", thumbnail
                )
                random_sleep(0.3, 0.6)

                driver.execute_script(  # pyright: ignore[reportUnknownMemberType]
                    "arguments[0].click();", thumbnail
                )
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
                    "img.n3VNCb",  # Alternative Google selector
                    "img.iPVvYb",  # Simplified selector
                    "img[jsname='kn3ccd']",  # Another Google selector
                    "img[jsname='HiaYvf']",  # Yet another variant
                    "div[data-id] img",  # Images inside preview divs
                    "a[jsname='sTFXNd'] img",  # Images in preview links
                ]

                found_image = False

                # First try specific selectors
                for img_selector in img_selectors:
                    try:
                        actual_images = driver.find_elements(
                            By.CSS_SELECTOR, img_selector
                        )

                        for actual_image in actual_images:
                            src = actual_image.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                "src"
                            ) or actual_image.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                "data-src"
                            )

                            if not src or src in downloaded_urls:
                                continue

                            if (
                                "data:image/gif" in src
                                or "data:image/svg" in src
                                or len(src) < 100
                            ):
                                continue

                            try:
                                width = actual_image.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                    "naturalWidth"
                                ) or actual_image.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                    "width"
                                )
                                height = actual_image.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                    "naturalHeight"
                                ) or actual_image.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                    "height"
                                )
                                if width and height:
                                    if int(width) < 100 or int(height) < 100:
                                        continue
                            except:
                                pass  # If we can't get dimensions, try downloading anyway

                            if (
                                "http" in src
                                or "data:image/jpeg" in src
                                or "data:image/png" in src
                            ):
                                if download_image(
                                    src, query_folder, f"img_{image_count}"
                                ):
                                    downloaded_urls.add(src)
                                    image_count += 1
                                    images_downloaded_this_round += 1
                                    processed_indices.add(idx)
                                    logger.info(
                                        f"Downloaded {image_count}/{num_images} for '{query}' using selector: {img_selector}"
                                    )
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
                        valid_images: list[tuple[WebElement, str, int]] = []
                        for img in all_images:
                            try:
                                src = img.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                    "src"
                                ) or img.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                    "data-src"
                                )
                                if not src or src in downloaded_urls:
                                    continue

                                if (
                                    "data:image/gif" in src
                                    or "data:image/svg" in src
                                    or len(src) < 100
                                ):
                                    continue

                                # Try to get image size
                                width = (
                                    img.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                        "naturalWidth"
                                    )
                                    or img.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                        "width"
                                    )
                                    or 0
                                )
                                height = (
                                    img.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                        "naturalHeight"
                                    )
                                    or img.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                        "height"
                                    )
                                    or 0
                                )

                                try:
                                    width = int(width)
                                    height = int(height)
                                except:
                                    width = 0
                                    height = 0

                                if width >= 500 and height >= 500:
                                    valid_images.append((img, src, width * height))
                            except:
                                continue

                        # Sort by size (largest first)
                        valid_images.sort(key=lambda x: x[2], reverse=True)

                        # Try to download the largest valid image
                        for img, src, _ in valid_images[:3]:  # Try top 3 largest
                            if (
                                "http" in src
                                or "data:image/jpeg" in src
                                or "data:image/png" in src
                            ):
                                if download_image(
                                    src, query_folder, f"img_{image_count}"
                                ):
                                    downloaded_urls.add(src)
                                    image_count += 1
                                    images_downloaded_this_round += 1
                                    processed_indices.add(idx)
                                    logger.info(
                                        f"Downloaded {image_count}/{num_images} for '{query}' using generic search"
                                    )
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
