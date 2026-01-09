from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger_config import logger
from utils import random_sleep, download_image
import os
import time
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
    logger.info(f"Starting high-resolution scrape for: {query}")

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
                    (By.CSS_SELECTOR, "img.YQ4gaf, img.Q4LuWd, img.rg_i")
                )
            )
        except Exception as e:
            logger.error(f"Timeout waiting for thumbnails: {e}")
            break

        thumbnail_selectors = ["img.YQ4gaf", "img.Q4LuWd", "img.rg_i"]
        thumbnails = []
        active_selector = None

        for selector in thumbnail_selectors:
            thumbnails = driver.find_elements(By.CSS_SELECTOR, selector)
            if thumbnails:
                active_selector = selector
                break

        if not thumbnails:
            logger.warning("No thumbnails found, scrolling...")
            scroll_page(driver, 3)
            scroll_count += 1
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

                # Click the thumbnail to open the preview pane
                driver.execute_script(  # pyright: ignore[reportUnknownMemberType]
                    "arguments[0].scrollIntoView({block: 'center'});", thumbnail
                )
                random_sleep(0.5, 1)
                driver.execute_script(  # pyright: ignore[reportUnknownMemberType]
                    "arguments[0].click();", thumbnail
                )
                random_sleep(1.5, 2.5)

                # Find the high-res image element and the visit link
                # Google uses jsname="kn3ccd" for the large preview image
                try:
                    preview_img = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "img[jsname='kn3ccd']")
                        )
                    )

                    # Wait for the high-resolution URL to load into the src attribute
                    high_res_url = None
                    for _ in range(15):  # Wait up to 15 seconds
                        src = preview_img.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                            "src"
                        )
                        if (
                            src
                            and "gstatic.com" not in src
                            and not src.startswith("data:")
                        ):
                            high_res_url = src
                            break
                        time.sleep(1)

                    if not high_res_url:
                        logger.warning(
                            f"Could not get high-res URL for thumbnail {idx}"
                        )
                        processed_indices.add(idx)
                        continue

                    # Find the 'Visit' button link
                    # Common selectors for the visit link on the preview pane
                    visit_selectors = ["a.umNKYc", "[jsname='St5Dhe'] a", "a.YsLeY"]
                    visit_url = None
                    for v_sel in visit_selectors:
                        try:
                            v_el = driver.find_element(By.CSS_SELECTOR, v_sel)
                            visit_url = v_el.get_attribute(  # pyright: ignore[reportUnknownMemberType]
                                "href"
                            )
                            if visit_url:
                                break
                        except:
                            continue

                    if visit_url:
                        logger.info(
                            f"Visiting source website for image {image_count+1}: {visit_url}"
                        )
                        # Open visit URL in a new tab
                        driver.execute_script(  # pyright: ignore[reportUnknownMemberType]
                            "window.open(arguments[0], '_blank');", visit_url
                        )
                        driver.switch_to.window(driver.window_handles[-1])
                        random_sleep(2, 4)  # Allow page to load and cookies to set

                        # Now open the image itself in a new tab as requested
                        logger.info(f"Opening image in new tab: {high_res_url}")
                        driver.execute_script(  # pyright: ignore[reportUnknownMemberType]
                            "window.open(arguments[0], '_blank');", high_res_url
                        )
                        driver.switch_to.window(driver.window_handles[-1])
                        random_sleep(1, 2)

                        # Download the image from the direct link
                        if download_image(
                            high_res_url, query_folder, f"img_{image_count}"
                        ):
                            image_count += 1
                            images_downloaded_this_round += 1
                            downloaded_urls.add(high_res_url)
                            logger.info(
                                f"Successfully downloaded high-res image {image_count}"
                            )

                        # Close extra tabs and return to main
                        while len(driver.window_handles) > 1:
                            driver.switch_to.window(driver.window_handles[-1])
                            driver.close()
                        driver.switch_to.window(main_window)
                    else:
                        # Fallback: Just download the high_res_url if visit link not found
                        if download_image(
                            high_res_url, query_folder, f"img_{image_count}"
                        ):
                            image_count += 1
                            images_downloaded_this_round += 1
                            downloaded_urls.add(high_res_url)
                            logger.info(
                                f"Downloaded via high-res URL directly (no visit link)"
                            )

                    processed_indices.add(idx)

                except Exception as e:
                    logger.debug(f"High-res workflow failed for thumbnail {idx}: {e}")
                    processed_indices.add(idx)
                    continue

            except Exception as e:
                logger.error(f"Error processing thumbnail {idx}: {e}")
                processed_indices.add(idx)
                continue

        if images_downloaded_this_round == 0:
            logger.info("No new high-res images found this round. Scrolling...")
            scroll_page(driver, 3)
            scroll_count += 1
            random_sleep(1, 2)

    logger.info(f"Finished. Total images downloaded: {image_count}")
