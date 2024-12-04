import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time

def sanitize_folder_name(folder_name):
    """
    Sanitize the folder name by removing invalid characters for the file system.

    Args:
        folder_name (str): Original folder name.

    Returns:
        str: Sanitized folder name.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', folder_name)

def scroll_to_bottom(driver):
    """
    Scroll to the bottom of the page to load all images.

    Args:
        driver: Selenium WebDriver instance.
    """
    scroll_pause_time = 2  # Pause time between scrolls
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for new content to load
        time.sleep(scroll_pause_time)

        # Check the new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def download_pins(board_url):
    """
    Download pins from a Pinterest board using Selenium and save them in a folder.

    Args:
        board_url (str): URL of the Pinterest board.
    """
    # Configure Selenium WebDriver for Firefox
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service("C:/tools/selenium/geckodriver.exe")  # Update with the path to your geckodriver
    driver = webdriver.Firefox(service=service, options=options)

    try:
        # Load the Pinterest board URL
        driver.get(board_url)
        print("Loading Pinterest board...")

        # Scroll to load all images on the board
        scroll_to_bottom(driver)

        # Extract page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract the board name from the title tag
        title = soup.title.string.strip() if soup.title else "Pinterest_Board"
        folder_name = sanitize_folder_name(title)
        os.makedirs(folder_name, exist_ok=True)
        print(f"Downloading pins to folder: {folder_name}")

        # Find all image elements
        img_tags = soup.find_all("img")
        downloaded_count = 0

        for index, img_tag in enumerate(img_tags):
            try:
                # Extract the image URL
                img_url = img_tag.get("src") or img_tag.get("data-src")
                if not img_url or not (".jpg" in img_url or ".png" in img_url):
                    continue  # Skip invalid URLs

                # Fetch the image
                img_response = requests.get(img_url, stream=True)
                if img_response.status_code != 200:
                    print(f"Failed to download image: {img_url}")
                    continue

                # Open the image
                img_data = BytesIO(img_response.content)
                img = Image.open(img_data)

                # Save the image
                img_name = os.path.join(folder_name, f"pin_{downloaded_count + 1}.jpg")
                img.save(img_name, format="JPEG")
                downloaded_count += 1
                print(f"Downloaded and saved: {img_name}")
            except Exception as e:
                print(f"Error downloading or processing an image: {e}")

        if downloaded_count == 0:
            print("No valid pins found.")
    except Exception as e:
        print(f"Error fetching the board: {e}")
    finally:
        driver.quit()

    print("Download completed.")

# This the 'UI' section
if __name__ == "__main__":
   
    board_url = input("Enter the Pinterest board URL: ")

    download_pins(board_url)
