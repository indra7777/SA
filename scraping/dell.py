from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime

def setup_driver():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        raise

def get_product_title(driver):
    try:
        title_element = driver.find_element(By.ID, "page-title")
        return title_element.text.strip()
    except:
        return "Title Not Found"

def get_product_images(driver):
    try:
        thumbnail_buttons = driver.find_elements(By.CSS_SELECTOR, ".thumb-list button")
        for button in thumbnail_buttons:
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
            except:
                continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        image_elements = soup.select("figure[data-full-img]")

        image_urls = []
        for img in image_elements:
            img_url = img.get("data-full-img")
            if img_url and not img_url.startswith("data:image"):
                full_url = "https:" + img_url if img_url.startswith("//") else img_url
                image_urls.append(full_url)

        return image_urls
    except Exception as e:
        print(f"Error getting product images: {e}")
        return []

def get_product_specs(driver, product_url):
    try:
        specs = []
        specs_url = product_url + "#tech-specs-anchor"
        driver.get(specs_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        specs_container = soup.find("div", {"id": "tech-spec-container"})

        if specs_container:
            specs_list = specs_container.find_all("li", class_="mb-2")
            for spec in specs_list:
                key = spec.find("div", class_="h5 font-weight-bold mb-0")
                value = spec.find("p")
                if key and value:
                    specs.append(f"{key.text.strip()}: {value.text.strip()}")

        return specs
    except Exception as e:
        print(f"Error getting product specifications: {e}")
        return []

def get_product_reviews(driver, product_url):
    reviews = []
    try:
        ratings_url = product_url + "#ratings_section"
        driver.get(ratings_url)
        
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'ratings_section')))

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                if driver.find_elements(By.CLASS_NAME, "pr-review"):
                    break
                driver.switch_to.default_content()
            except:
                continue

        while True:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_divs = soup.find_all('div', class_='pr-review')

            for review in review_divs:
                title = review.find('span', class_='pr-rd-review-headline')
                text = review.find('p', class_='pr-rd-description-text')
                if title and text:
                    reviews.append({
                        'title': title.text.strip(),
                        'review': text.text.strip()
                    })

            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'pr-rd-pagination-btn--next'))
                )
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
            except:
                break

        driver.switch_to.default_content()
    except Exception as e:
        print(f"Error getting product reviews: {e}")
    
    return reviews

def save_to_csv(data, filename_prefix="dell_product"):
    try:
        os.makedirs('./data', exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./data/{filename_prefix}_{timestamp}.csv"
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        return filename
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return None

def scrape_dell_product(url):
    """Main function to scrape Dell product details and reviews"""
    try:
        driver = setup_driver()
        driver.get(url)
        time.sleep(3)

        # Gather all product information
        product_data = {
            'title': get_product_title(driver),
            'images': get_product_images(driver),
            'specifications': get_product_specs(driver, url),
            'reviews': get_product_reviews(driver, url)
        }

        # Save data to CSV
        filename = save_to_csv([{
            'product_title': product_data['title'],
            'product_images': ', '.join(product_data['images']),
            'specifications': ', '.join(product_data['specifications']),
            'review_title': review['title'],
            'review_text': review['review']
        } for review in product_data['reviews']] if product_data['reviews'] else [{
            'product_title': product_data['title'],
            'product_images': ', '.join(product_data['images']),
            'specifications': ', '.join(product_data['specifications']),
            'review_title': 'No Reviews',
            'review_text': 'No Reviews'
        }])

        driver.quit()
        return filename

    except Exception as e:
        print(f"Error in scrape_dell_product: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

if __name__ == "__main__":
    product_url = "https://www.dell.com/en-in/shop/shop-all-deals/inspiron-15-laptop/spd/inspiron-15-3530-laptop/oin353034071rins1m"
    filename = scrape_dell_product(product_url)
    if filename:
        print(f"Data saved to {filename}")
    else:
        print("Failed to scrape product data")
