import time
import csv
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def get_text_or_empty(soup_element):
    return soup_element.text.strip() if soup_element else ""

def scrape_nike_product(url):
    """
    Scrape Nike product details and reviews, save to CSV, and return the review CSV filename.
    """
    # Step 1: Setup headless Chrome browser
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("start-maximized")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    time.sleep(5)  # Allow time for the page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract product details
    title = get_text_or_empty(soup.find('h1', {'data-testid': 'product_title'}))
    subtitle = get_text_or_empty(soup.find('h2', {'data-testid': 'product_subtitle'}))
    image_url = soup.find('img', {'data-testid': 'HeroImg'})['src'] if soup.find('img', {'data-testid': 'HeroImg'}) else ""
    price = get_text_or_empty(soup.find('span', {'data-testid': 'currentPrice-container'}))
    description = get_text_or_empty(soup.find('p', {'data-testid': 'product-description'}))
    benefits_list = soup.find_all('ul', {'data-testid': 'benefit-list'})
    benefits = [li.text.strip() for li in benefits_list[0].find_all('li')] if len(benefits_list) >= 1 else []
    product_details = [li.text.strip() for li in benefits_list[1].find_all('li')] if len(benefits_list) >= 2 else []

    # Step 2: Click the Reviews dropdown
    try:
        summary = wait.until(EC.element_to_be_clickable((By.XPATH, "//summary[.//h4[contains(text(),'Reviews')]]")))
        driver.execute_script("arguments[0].click();", summary)
        time.sleep(2)
    except Exception as e:
        print("Error opening reviews dropdown:", str(e))

    # Step 3: Click "More Reviews" button
    try:
        more_reviews = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='more-reviews-button']")))
        driver.execute_script("arguments[0].click();", more_reviews)
        time.sleep(3)
    except Exception as e:
        print("Error opening full review page:", str(e))

    # Step 4: Get total number of reviews
    try:
        review_count_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tt-c-reviews-summary__heading")))
        total_reviews = int(review_count_elem.text.strip().split()[0])
        print(f"Total reviews found: {total_reviews}")
    except Exception as e:
        print("Could not find total review count:", str(e))
        total_reviews = 0

    # Calculate total pages
    total_pages = 1 if total_reviews <= 10 else 1 + ((total_reviews - 10 + 19) // 20)

    # Step 5: Scrape reviews
    titles = []
    texts = []
    for page in range(total_pages):
        print(f"Scraping page {page + 1} of {total_pages}")
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".tt-c-review")))
            time.sleep(1)
            # Click all "Read More" buttons
            for btn in driver.find_elements(By.CSS_SELECTOR, "button.tt-c-review__text-expand"):
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.3)
                except:
                    pass
            # Re-parse page content
            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_blocks = soup.select(".tt-c-review")
            for block in review_blocks:
                review_title = get_text_or_empty(block.select_one("div.tt-c-review__heading-text"))
                text = get_text_or_empty(block.select_one("span.tt-c-review__text-content"))
                if text:
                    titles.append(review_title if review_title else "No Title")
                    texts.append(text)
        except Exception as e:
            print("Error scraping page:", str(e))
            continue
        # Click next page
        if page < total_pages - 1:
            try:
                next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.tt-o-pagination__next")))
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(3)
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break
    driver.quit()

    # Store product details in DataFrame
    df_product = pd.DataFrame({
        "product_title": [title],
        "subtitle": [subtitle],
        "image_url": [image_url],
        "price": [price],
        "description": [description],
        "benefits": ['; '.join(benefits)],
        "product_details": ['; '.join(product_details)],
        "total_reviews": [len(titles)]
    })
    df_reviews = pd.DataFrame({"review_title": titles, "review_text": texts})

    # Save to CSV in ./data directory
    os.makedirs('./data', exist_ok=True)
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    product_filename = f"./data/nike_product_details_{timestamp}.csv"
    reviews_filename = f"./data/nike_product_reviews_{timestamp}.csv"
    df_product.to_csv(product_filename, index=False)
    df_reviews.to_csv(reviews_filename, index=False)
    print(f"✅ Product details saved to {product_filename}")
    print(f"✅ {len(titles)} reviews saved to {reviews_filename}")
    return reviews_filename
