from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from datetime import datetime

# Configure WebDriver
def setup_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)
    return driver


# Function to navigate to the product page
def open_product_page(driver, url):
    driver.get(url)
    time.sleep(3)


# Function to find and click "All Reviews" button
def click_all_reviews(driver):
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div._23J90q.RcXBOT"))
        )
        button.click()
        time.sleep(3)
        return True
    except Exception as e:
        print(f"Error clicking 'All Reviews' button: {e}")
        return False


# Function to clean review text by removing "READ MORE"
def clean_review_text(text):
    """Remove READ MORE from review text"""
    # Use regex to remove READ MORE and any whitespace before it
    cleaned_text = re.sub(r'\s*READ MORE$', '', text.strip())
    return cleaned_text


# Function to extract only review text
def extract_reviews(driver):
    """Scrape only review text from the current page and remove READ MORE"""
    reviews = []

    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find all review elements
    review_elements = soup.select("div.ZmyHeo")

    if not review_elements:
        print("No reviews found on the page.")
        return []

    for review in review_elements:
        try:
            # Extract only review text
            review_text = review.select_one("div div").text.strip()
            if review_text:  # Only add non-empty reviews
                # Clean the review text by removing READ MORE
                cleaned_text = clean_review_text(review_text)
                reviews.append({"Review": cleaned_text})
        except Exception as e:
            print(f"Error extracting review: {e}")
            continue

    return reviews


# Function to check if next button is available and click it
def go_to_next_page(driver):
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='_9QVEpD']/span[text()='Next']"))
        )

        # Check if button is disabled
        parent_elem = next_button.find_element(By.XPATH, "..")
        if 'disabled' in parent_elem.get_attribute('class'):
            print("Next button is disabled. Reached end of reviews.")
            return False

        # Scroll and click the next button
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(2)
        return True
    except (TimeoutException, NoSuchElementException):
        print("Next button not found or not accessible.")
        return False


# Function to save reviews to CSV
def save_to_csv(all_reviews, filename_prefix="reviews"):
    if all_reviews:
        # Ensure the data directory exists
        os.makedirs('./data', exist_ok=True)

        # Generate unique filename with date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./data/{filename_prefix}_{timestamp}.csv"

        # Save to CSV
        df = pd.DataFrame(all_reviews)
        df.to_csv(filename, index=False, encoding="utf-8")
        
        print(f"All {len(all_reviews)} reviews saved to {filename}")
        return filename
    else:
        print("No reviews found to save.")


# Main function
def scrape_flipkart_reviews(url, max_pages=None, empty_page_limit=3):
    """
    Scrape Flipkart reviews

    Parameters:
    url (str): URL of the product page
    max_pages (int, optional): Maximum number of pages to scrape
    empty_page_limit (int): Stop after this many consecutive empty pages
    """
    driver = setup_driver()
    all_reviews = []
    page_count = 1
    empty_page_count = 0

    try:
        print(f"Opening product page: {url}")
        open_product_page(driver, url)

        if click_all_reviews(driver):
            continue_scraping = True

            while continue_scraping:
                print(f"Scraping page {page_count}...")
                reviews = extract_reviews(driver)

                if reviews:
                    all_reviews.extend(reviews)
                    empty_page_count = 0  # Reset empty page counter
                    print(f"Found {len(reviews)} reviews on page {page_count}")
                    print(f"Total reviews collected: {len(all_reviews)}")
                else:
                    empty_page_count += 1
                    print(f"No reviews found on page {page_count}. Empty page count: {empty_page_count}")
                    if empty_page_count >= empty_page_limit:
                        print(f"Reached {empty_page_limit} consecutive empty pages. Stopping.")
                        break

                # Stop if reached max_pages
                if max_pages and page_count >= max_pages:
                    print(f"Reached maximum page limit ({max_pages})")
                    break

                # Try to go to next page
                continue_scraping = go_to_next_page(driver)
                page_count += 1

            # Save all collected reviews
            filename = save_to_csv(all_reviews)
            print(f"Completed scraping {len(all_reviews)} reviews from {page_count - 1} pages")
            return filename
        else:
            print("Could not open reviews page.")
    except Exception as e:
        print(f"An error occurred: {e}")
        # Save whatever reviews were collected
        if all_reviews:
            save_to_csv(all_reviews, f"partial_reviews_{int(time.time())}.csv")
            print("Saved partial results due to error")
    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    product_url = "https://www.flipkart.com/frontech-ultima-series-60-96-cm-24-inch-full-hd-led-backlit-va-panel-monitor-mon-0072/p/itm3f6383037d9d6?pid=MONGWNGHYY7EHAZ2&lid=LSTMONGWNGHYY7EHAZ2KOYFZN&marketplace=FLIPKART&store=6bo%2Fg0i%2F9no&srno=b_1_1&otracker=browse&otracker1=hp_rich_navigation_PINNED_neo%2Fmerchandising_NA_NAV_EXPANDABLE_navigationCard_cc_3_L2_view-all&fm=organic&iid=en_xCfdgqlQFXayOaFKpzGsnigxkIZUlz-t5dhyzgu7xnOxUc5oA2Fx1Rne5TM-RxrEcpoMZhuMi4iHCak2TjqRBw%3D%3D&ppt=hp&ppn=homepage&ssid=b7utg4l8j40000001740137773854"

    # To scrape with default settings (all pages until disabled button or 3 empty pages)
    # scrape_flipkart_reviews(product_url)

    # Examples with different configurations:
    scrape_flipkart_reviews(product_url, max_pages=10)  # Limit to 10 pages
#     scrape_flipkart_reviews(product_url, empty_page_limit=5)  # Stop after 5 empty pages
#     scrape_flipkart_reviews(product_url, max_pages=20, empty_page_limit=2)  # Custom limits
