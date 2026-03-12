from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os


# ----------------------------
# Load failed links
# ----------------------------
def load_failed_links():

    if not os.path.exists("failed_links.txt"):
        print("failed_links.txt not found")
        return []

    with open("failed_links.txt", "r") as f:
        links = [line.strip() for line in f if line.strip()]

    return links


# ----------------------------
# Save product to CSV
# ----------------------------
def save_product(product_data, filename):

    df = pd.DataFrame([product_data])

    if os.path.isfile(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, mode='w', header=True, index=False)


# ----------------------------
# Scrape single product
# ----------------------------
def scrape_product(driver, wait, link):

    driver.get(link)

    name = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'h1.e-vbt7pb'))
    ).text

    price = ""

    for locator in [
        (By.CSS_SELECTOR,"div.e-175s8ne"),
        (By.ID,"sale_price"),
        (By.ID,"regular_price"),
    ]:
        try:
            price = driver.find_element(*locator).text
            if price:
                break
        except:
            continue

    images = driver.find_elements(By.CSS_SELECTOR,'div.e-2szg1 div picture img')

    img_links = []

    for img in images[:4]:

        srcset = img.get_attribute('srcset')

        if srcset:
            img_links.append(srcset.split(',')[-1].strip().split(" ")[0])

    details = {}

    try:
        about = driver.find_element(By.CSS_SELECTOR,'div.e-b8kzem')
        a = about.text.split('\n')

        if len(a) > 1:
            details[a[0]] = ', '.join(a[1:])
    except:
        pass

    product_data = {
        "Name": name,
        "Price": price,
        "Images": ", ".join(img_links),
        **details
    }

    return product_data


# ----------------------------
# Main retry function
# ----------------------------
def retry_failed_links():

    category_name = input("Enter category name (same CSV name): ")

    filename = f"{category_name}.csv"

    links = load_failed_links()

    if not links:
        print("No failed links to retry")
        return

    print(f"Retrying {len(links)} failed links\n")

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver,10)

    still_failed = []

    for i,link in enumerate(links):

        try:

            product_data = scrape_product(driver,wait,link)

            save_product(product_data,filename)

            print(f"Recovered product {i+1}")

        except Exception as e:

            print(f"Still failing: {link}")

            still_failed.append(link)

    driver.quit()

    # Rewrite failed links file with remaining failures
    with open("failed_links.txt","w") as f:

        for link in still_failed:
            f.write(link+"\n")

    print("\nRetry completed")
    print(f"{len(still_failed)} links still failed")


if __name__ == "__main__":

    retry_failed_links()