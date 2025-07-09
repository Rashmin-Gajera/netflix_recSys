import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_images_from_page(url, num_images=5, save_dir="."):
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

# Example usage
# image_page_url = "https://www.imdb.com/title/tt3799232/mediaviewer/rm1883393024/?ref_=tt_ov_i"
image_page_url = "https://www.imdb.com/title/tt9432978/"

scrape_images_from_page(image_page_url)
