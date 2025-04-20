from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from datetime import datetime

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    return webdriver.Chrome(options=options)

def scrape_nykaa_product(url):
    driver = setup_driver()
    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Get product details
        title_tag = soup.find('h1', class_='css-1gc4x7i')
        title = title_tag.get_text(strip=True) if title_tag else "Title not found"

        img_div = soup.find('div', class_='productSelectedImage')
        img_tag = img_div.find('img') if img_div else None
        image_url = img_tag['src'] if img_tag else "Image not found"

        # Get description and ratings
        description = get_product_description(soup)
        total_ratings, total_reviews = get_ratings_reviews_count(soup)

        # Get reviews
        reviews = get_product_reviews(driver)

        return save_to_csv({
            'title': title,
            'image_url': image_url,
            'description': description,
            'total_ratings': total_ratings,
            'total_reviews': total_reviews,
            'reviews': reviews
        })

    except Exception as e:
        print(f"Error scraping product: {e}")
        return None
    finally:
        driver.quit()

def get_product_description(soup):
    desc_element = soup.find('div', class_='product-description')
    return desc_element.get_text(strip=True) if desc_element else "Description not found"

def get_ratings_reviews_count(soup):
    try:
        ratings_element = soup.find('div', class_='rating-count')
        reviews_element = soup.find('div', class_='reviews-count')
        return (
            ratings_element.get_text(strip=True) if ratings_element else "0",
            reviews_element.get_text(strip=True) if reviews_element else "0"
        )
    except:
        return "0", "0"

def get_product_reviews(driver):
    reviews = []
    try:
        # Navigate to reviews section
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        read_more_button = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.css-1xv8iu0"))
        )
        full_reviews_url = read_more_button.get_attribute("href")
        if full_reviews_url.startswith("/"):
            full_reviews_url = "https://www.nykaa.com" + full_reviews_url
        
        driver.get(full_reviews_url)
        time.sleep(3)

        seen_texts = set()
        while True:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_sections = soup.find_all("section", class_="css-1v6g5ho")

            new_reviews_found = False
            for section in review_sections:
                title_tag = section.find("div", class_="css-tm4hnq")
                text_tag = section.find("p", class_="css-1n0nrdk")

                title_text = title_tag.get_text(strip=True) if title_tag else ""
                review_text = text_tag.get_text(strip=True) if text_tag else ""

                if review_text and review_text not in seen_texts:
                    seen_texts.add(review_text)
                    reviews.append({
                        'title': title_text,
                        'text': review_text
                    })
                    new_reviews_found = True

            if not new_reviews_found:
                break

            try:
                load_more_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.css-1a51j15 > button.css-u04n34"))
                )
                driver.execute_script("arguments[0].click();", load_more_btn)
                time.sleep(2)
            except:
                break

    except Exception as e:
        print(f"Error getting reviews: {e}")
    
    return reviews

def save_to_csv(data, filename_prefix="nykaa_product"):
    try:
        os.makedirs('./data', exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./data/{filename_prefix}_{timestamp}.csv"
        
        # Prepare data for DataFrame
        rows = []
        if data['reviews']:
            rows = [{
                'product_title': data['title'],
                'image_url': data['image_url'],
                'description': data['description'],
                'total_ratings': data['total_ratings'],
                'total_reviews': data['total_reviews'],
                'review_title': review['title'],
                'review_text': review['text']
            } for review in data['reviews']]
        else:
            rows.append({
                'product_title': data['title'],
                'image_url': data['image_url'],
                'description': data['description'],
                'total_ratings': data['total_ratings'],
                'total_reviews': data['total_reviews'],
                'review_title': 'No Reviews',
                'review_text': 'No Reviews'
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8')
        return filename
    
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return None

if __name__ == "__main__":
    url = "https://www.nykaa.com/moroccanoil-treatment-oil/p/8551062"
    filename = scrape_nykaa_product(url)
    if filename:
        print(f"Data saved to {filename}")
    else:
        print("Failed to scrape product data")
