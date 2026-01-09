from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
WEBSITE_LOAD_TIMEOUT = int(os.getenv("WEBSITE_LOAD_TIMEOUT", 10))


def scroll_page(driver: webdriver.Chrome, scrolls: int = 2):
    logger.info(f"Scrolling page to load more results...")
    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_sleep(1.5, 2.5)

    try:
        # Modern 'Show more' button selectors and text search
        possible_selectors = [
            ".mye4qd",
            ".LZ4I",
            "input[value='Show more results']",
            ".kSFCof.MagqMc.U48fD",
            "div[role='button'][aria-label='Show more results']",
        ]

        found_btn = False
        for selector in possible_selectors:
            try:
                show_more_btn = driver.find_element(By.CSS_SELECTOR, selector)
                if show_more_btn.is_displayed():
                    logger.info(
                        f"Clicking 'Show more results' button (selector: {selector})"
                    )
                    driver.execute_script("arguments[0].click();", show_more_btn)
                    random_sleep(2, 3)
                    found_btn = True
                    break
            except:
                continue

        if not found_btn:
            # Fallback text search using JavaScript to find button with 'Show more'
            driver.execute_script(
                """
                const btns = Array.from(document.querySelectorAll('button, div[role="button"], input[type="button"]'));
                const showMore = btns.find(b => b.innerText && (b.innerText.toLowerCase().includes('show more') || b.innerText.includes('नतीजा हेर्नुहोस्') || b.innerText.includes('थप')));
                if (showMore) {
                    showMore.scrollIntoView();
                    showMore.click();
                }
            """
            )
            random_sleep(1, 2)

    except Exception as e:
        logger.debug(f"Scroll/Show-more interaction error: {e}")


def scrape_images(driver: webdriver.Chrome, query: str, num_images: int):
    logger.info(f"Starting high-resolution scrape for: {query}")
    driver.set_page_load_timeout(WEBSITE_LOAD_TIMEOUT)

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
            # Wait for thumbnails that are likely actual results (inside .mNsIhb)
            _ = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".mNsIhb img.YQ4gaf, .H8uYec img.YQ4gaf")
                )
            )
        except Exception as e:
            logger.error(f"Timeout waiting for thumbnails: {e}")
            break

        # Prioritize selectors that are unique to search results, not chips
        thumbnail_selectors = [".mNsIhb img.YQ4gaf", ".H8uYec img.YQ4gaf", "img.YQ4gaf"]
        thumbnails = []
        active_selector = None

        for selector in thumbnail_selectors:
            all_found = driver.find_elements(By.CSS_SELECTOR, selector)
            # Filter out elements that are inside chip containers (nPDzT or T3FoJb)
            valid_thumbnails = []
            for img in all_found:
                try:
                    # Check if the image is inside a suggestion chip or related search
                    if img.find_elements(
                        By.XPATH,
                        "./ancestor::a[contains(@class, 'nPDzT') or contains(@class, 'T3FoJb') or contains(@class, 'bqW4cb')]",
                    ):
                        continue
                    valid_thumbnails.append(img)
                except:
                    valid_thumbnails.append(img)

            if valid_thumbnails:
                thumbnails = valid_thumbnails
                active_selector = selector
                break

        if not thumbnails:
            logger.warning("No valid thumbnails found, scrolling...")
            scroll_page(driver, 2)
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
                        try:
                            # Use new tabs with driver.get to enforce timeout
                            driver.execute_script("window.open('', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])
                            driver.get(visit_url)
                            random_sleep(2, 4)

                            # Now open the image itself in a new tab
                            logger.info(f"Opening image in new tab: {high_res_url}")
                            driver.execute_script("window.open('', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])
                            driver.get(high_res_url)
                            random_sleep(1, 2)

                            # Download the image
                            if download_image(
                                high_res_url, query_folder, f"img_{image_count}"
                            ):
                                image_count += 1
                                images_downloaded_this_round += 1
                                downloaded_urls.add(high_res_url)
                                logger.info(
                                    f"Successfully downloaded high-res image {image_count}"
                                )
                        except TimeoutException:
                            logger.warning(
                                f"Website or image took too long to load (>{WEBSITE_LOAD_TIMEOUT}s), skipping: {visit_url}"
                            )
                        except Exception as e:
                            logger.error(f"Error visiting source website: {e}")
                        finally:
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
