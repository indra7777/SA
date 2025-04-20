import time
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def scrape_myntra_product(product_url):
    """
    Scrape Myntra product details and reviews, save to CSV, and return the review CSV filename.
    """
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    product_data = {}
    try:
        # Step 1: Product Info
        driver.get(product_url)
        title = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pdp-title"))).text
        product_data["product_title"] = title
        images = driver.find_elements(By.CSS_SELECTOR, ".image-grid-imageContainer .image-grid-image")
        image_urls = []
        for img in images:
            style = img.get_attribute("style")
            if "url" in style:
                start = style.find('("') + 2
                end = style.find('")')
                image_urls.append(style[start:end])
        product_data["image_urls"] = ", ".join(image_urls)
        try:
            see_more = driver.find_element(By.CLASS_NAME, "index-showMoreText")
            driver.execute_script("arguments[0].click();", see_more)
            time.sleep(1)
        except:
            pass
        try:
            details_section = driver.find_element(By.CLASS_NAME, "pdp-product-description-content")
            product_data["product_details"] = details_section.text.replace("\n", " ")
        except:
            product_data["product_details"] = "N/A"
        try:
            size_fit = driver.find_element(By.CLASS_NAME, "pdp-sizeFitDescContent")
            product_data["size_fit"] = size_fit.text.replace("\n", " ")
        except:
            product_data["size_fit"] = "N/A"
        try:
            material = driver.find_elements(By.CLASS_NAME, "pdp-sizeFitDescContent")
            if len(material) > 1:
                product_data["material_and_care"] = material[1].text.replace("\n", " ")
            else:
                product_data["material_and_care"] = "N/A"
        except:
            product_data["material_and_care"] = "N/A"
        try:
            spec_keys = driver.find_elements(By.CLASS_NAME, "index-rowKey")
            spec_values = driver.find_elements(By.CLASS_NAME, "index-rowValue")
            for key, value in zip(spec_keys, spec_values):
                product_data[key.text.strip()] = value.text.strip()
        except:
            pass
        # Save product data
        os.makedirs('./data', exist_ok=True)
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        product_details_file = f"./data/myntra_product_data_{timestamp}.csv"
        with open(product_details_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Field", "Value"])
            for key, value in product_data.items():
                writer.writerow([key, value])
        # Step 2: Extract Product Code for Reviews
        product_code = driver.find_element(By.CLASS_NAME, "supplier-styleId").text.strip()
        review_url = f"https://www.myntra.com/reviews/{product_code}"
        driver.get(review_url)
        time.sleep(2)
        # Step 3: Scrape Reviews
        soup = BeautifulSoup(driver.page_source, "html.parser")
        total_reviews = int(re.search(r'\((\d+)\)', soup.find("div", class_="detailed-reviews-headline").text).group(1))
        reviews = set()
        last_scraped = 0
        retries = 0
        max_retries = 5
        while len(reviews) < total_reviews and retries < max_retries:
            for _ in range(5):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.3)
            time.sleep(1.2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            current_reviews = soup.find_all("div", class_="user-review-reviewTextWrapper")
            for r in current_reviews:
                reviews.add(r.text.strip())
            now_scraped = len(reviews)
            if now_scraped == last_scraped:
                retries += 1
            else:
                retries = 0
            last_scraped = now_scraped
        reviews_file = f"./data/myntra_reviews_{timestamp}.csv"
        df = pd.DataFrame(list(reviews), columns=["review_text"])
        df.to_csv(reviews_file, index=False, encoding="utf-8")
        return reviews_file
    except Exception as e:
        print("❌ Error:", e)
        return None
    finally:
        driver.quit()

# URL to scrape
PRODUCT_URL = "https://www.myntra.com/tshirts/u.s.+polo+assn.+denim+co./us-polo-assn-denim-co-brand-logo-printed-pure-cotton-slim-fit-t-shirt/27566344/buy"

reviews_file = scrape_myntra_product(PRODUCT_URL)
print(f"✅ Reviews saved to '{reviews_file}'")
