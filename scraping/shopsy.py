from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

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

def scrape_product_details(url):
    driver = setup_driver()
    driver.get(url)
    time.sleep(3)  # Allow time for page to load
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Extract product title
    title_element = soup.select_one("div.css-175oi2r.r-iphfwy div.css-146c3p1 span.css-1jxf684")
    product_title = title_element.text.strip() if title_element else "Title not found"
    
    # Extract image URL
    image_element = soup.select_one("div.css-175oi2r img")
    image_url = image_element["src"] if image_element else "Image not found"
    
    # Extract general product details
    details = {}
    general_info_elements = soup.select("div.css-175oi2r[style*='flex-direction: row']")
    for element in general_info_elements:
        key_element = element.select_one("div.r-1h7g6bg")
        value_element = element.select_one("div.r-xaq1zp")
        if key_element and value_element:
            details[key_element.text.strip()] = value_element.text.strip()
    
    driver.quit()
    
    return product_title, image_url, details

def save_to_csv(product_title, image_url, details, filename="shopsy_product_details.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Product Title", "Image URL"] + list(details.keys()))
        writer.writerow([product_title, image_url] + list(details.values()))
    print(f"Data has been successfully saved to {filename}")

if __name__ == "__main__":
    product_url = "https://www.shopsy.in/men-checkered-formal-green-shirt/p/itm2aaa83b443cb8?pid=XSRGQEYFBTTZK5XC&lid=LSTXSRGQEYFBTTZK5XCGEEZVC&marketplace=FLIPKART&q=men+clothing&store=clo"
    title, image, product_details = scrape_product_details(product_url)
    print(f"Title: {title}\nImage URL: {image}\nDetails: {product_details}")
    save_to_csv(title, image, product_details)
