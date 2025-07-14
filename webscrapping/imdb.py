import os
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import numpy as np

# Constants for input files
INPUT_FILE = "../datasets/netflix_v3.csv" #files for taking input
OUTPUT_FILE = "../datasets/netflix_v3.csv"

# Function to scrape images from IMDb
def scrape_images_from_page(url, num_images=1, save_dir="../static/posters/"):
    # Create save directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)  # Go to the provided URL

    # Find the anchor elements with the class 'ipc-lockup-overlay'
    anchor_elements = driver.find_elements(By.CSS_SELECTOR, "a.ipc-lockup-overlay")

    # Loop over the first num_images to extract href and load images
    for idx, anchor in enumerate(anchor_elements[:num_images]):
        href = anchor.get_attribute("href")  # Extract the URL from the href attribute
        print(f"Found href: {href}")

        # Visit the media viewer page (URL extracted from href)
        driver.get(href)

        # Wait for the image element to load on the media viewer page
        image_element = driver.find_element(By.CSS_SELECTOR, "img")  # Re-locate image element after navigation
        img_url = image_element.get_attribute("src")
        print(f"Found image URL: {img_url}")

        # Download the image and save it to the directory
        try:
            img_data = requests.get(img_url).content
            img_name = os.path.join(save_dir, f"image_{idx + 1}.jpg")  # Save as image_1.jpg, image_2.jpg, etc.
            with open(img_name, 'wb') as f:
                f.write(img_data)
            print(f"Saved {img_name}")
        except Exception as e:
            print(f"Failed to download image {idx + 1}: {e}")

    driver.quit()

# Main logic for scraping images
def main():
    df = pd.read_csv(INPUT_FILE)

    # Ensure 'fetched_images' column exists
    if 'fetched_images' not in df.columns:
        df['fetched_images'] = ""

    # Iterate and scrape images where missing
    for index, row in df.iterrows():
        if pd.notna(row['fetched_images']) and str(row['fetched_images']).strip() != "":
            print(f"Skipping '{row['title']}' - already has images. Index: {index}")
            continue

        imdb_url = f"https://www.imdb.com/title/{row['imdb_id']}/"  # Assuming 'imdb_id' exists in the dataset
        scrape_images_from_page(imdb_url, num_images=5, save_dir=f"images/{row['title']}")

        df.at[index, 'fetched_images'] = f"images/{row['title']}"  # Save path where images are stored
        print(f"Images for '{row['title']}' have been fetched and saved.")

        # Save after every 10 rows
        if (index + 1) % 10 == 0:
            df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

        # Add random sleep time to respect rate limits
        time.sleep(random.uniform(1, 2))

    # Final save after loop
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"\nAll images saved in '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
