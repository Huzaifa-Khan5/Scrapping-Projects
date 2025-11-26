from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

# ====== Configs ======
CSV_PATH = "iherb_products.csv"
TARGET_URL = "https://www.iherb.com/c/amino-acids-blends"
REQUIRED_COLUMNS = ["Name", "Price", "Image_URLs", "Product_Link", "scraped", "Description"]

# ====== Chrome Options ======
def get_driver(incognito=False):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    if incognito:
        options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #     "source": """
    #     Object.defineProperty(navigator, 'webdriver', {
    #         get: () => undefined
    #     })
    #     """
    # })
    return driver

# ====== Scroll Helper ======
def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(random.uniform(1, 2))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# ====== Load or Create CSV ======
if os.path.exists(CSV_PATH):
    try:
        existing_df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        for col in REQUIRED_COLUMNS:
            if col not in existing_df.columns:
                existing_df[col] = "" if col != "scraped" else True
        existing_df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
    except:
        existing_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
        existing_df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
else:
    existing_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    existing_df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')

# ====== Already Scraped Links ======
scraped_links = set(existing_df.loc[existing_df['scraped'] == True, 'Product_Link'].astype(str).tolist())

# ====== SCRAPE PRODUCTS (listing page) ======
driver = get_driver()
driver.get(TARGET_URL)
# scroll_page(driver)
time.sleep(2)
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

products = []

for item in soup.select("div.product-inner.product-inner-wide"):
    link_tag = item.select_one("a.product-link")
    product_link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ""
    if product_link and not product_link.startswith("http"):
        product_link = "https://pk.iherb.com" + product_link

    if product_link in scraped_links:
        continue

    name = item.select_one("div.product-title").get_text(strip=True) if item.select_one("div.product-title") else ""
    price = item.select_one("span.price").get_text(strip=True) if item.select_one("span.price") else ""
    # rating = item.select_one('meta[itemprop="ratingValue"]')['content'] if item.select_one('meta[itemprop="ratingValue"]') else ""

    products.append({
        "Name": name,
        "Price": price,
        # "Rating": rating,
        "Image_URLs": "",
        "Product_Link": product_link,
        "scraped": True,
        "Description": ""  # placeholder for now
    })

# ====== SAVE BASIC INFO ======
new_df = pd.DataFrame(products)

if not new_df.empty:
    new_df.to_csv(CSV_PATH, mode='a', index=False, header=False, encoding='utf-8-sig')
    print(f"➕ Appended {len(new_df)} new products to CSV.")
else:
    print("ℹ️ No new products to scrape.")

# ====== Utility to Extract Product Description ======
def extract_product_overview_text(soup):
    overview = soup.select_one('.product-overview')
    if not overview:
        return ""
    return overview.get_text(separator=' ', strip=True)

# ====== Re-Load with newly added products ======
updated_df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')

# ====== UPDATE EACH PRODUCT WITH THUMBNAIL & DESCRIPTION ======
print("\n🕵️ Fetching thumbnails and descriptions...\n")

for idx, row in updated_df.iterrows():
    if not row['Image_URLs'] or not row['Description']:
        try:
            browser = get_driver(incognito=True)
            browser.get(row['Product_Link'])
            time.sleep(8)

            browser.execute_script("""
                let modal = document.querySelector('.modal-wrap');
                if (modal) modal.remove();
            """)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            # Extract thumbnails
            thumbnail_urls = browser.execute_script("""
                const thumbnails = document.querySelectorAll('.thumbnail-item img');
                const urls = [];
                thumbnails.forEach((img, i) => {
                    if (i <= 2) {
                        let url = img.getAttribute('data-large-img') || img.getAttribute('src');
                        if (url) urls.push(url);
                    }
                });
                return urls;
            """)

            # Extract description
            description_text = extract_product_overview_text(soup)

            # Update DataFrame
            updated_df.at[idx, "Image_URLs"] = ", ".join(thumbnail_urls)
            updated_df.at[idx, "Description"] = description_text

            print(f"✅ {idx+1}. {row['Name'][:50]}... done")

            browser.quit()
        except Exception as e:
            print(f"❌ Error on {row['Product_Link']}: {e}")
            continue

# ====== SAVE FINAL DATA ======
updated_df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
print("\n💾 All product descriptions and thumbnails updated!\n")
