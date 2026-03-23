from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os


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
# Save failed links
# ----------------------------
def save_failed_link(link,filename):

    with open(f"{filename}_failed_links.txt", "a") as f:
        f.write(link + "\n")


# ----------------------------
# Scrape products (TAB METHOD)
# ----------------------------
def scrape_products(driver, wait, products_links, filename):

    for j, product_link in enumerate(products_links):

        try:
            # Open product in new tab
            driver.execute_script("window.open(arguments[0]);", product_link)

            driver.switch_to.window(driver.window_handles[1])

            name = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.e-vbt7pb'))
            ).text

            # -------- PRICE --------
            price = None

            for locator in [
                (By.CSS_SELECTOR, "div.e-7jsaf9 span"),
                (By.ID, "sale_price"),
                (By.ID, "regular_price")
            ]:
                try:
                    price = wait.until(
                        EC.presence_of_element_located(locator)
                    ).text
                    if price:
                        break
                except:
                    continue

            # -------- IMAGES --------
            images = driver.find_elements(By.CSS_SELECTOR, 'div.e-2szg1 div picture img')

            img_links = []

            for img in images[:4]:

                srcset = img.get_attribute('srcset')

                if srcset:
                    img_links.append(srcset.split(',')[-1].strip().split(" ")[0])

            # -------- DETAILS --------
            details = {}

            try:
                about = driver.find_element(By.CSS_SELECTOR, 'div.e-b8kzem')

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

            save_product(product_data, filename)

            print(f"Saved product {j+1}")

        except Exception as e:

            print(f"Error scraping: {product_link}")

            save_failed_link(product_link,filename)

        finally:

            driver.close()

            driver.switch_to.window(driver.window_handles[0])


# ----------------------------
# Pagination handler
# ----------------------------
def get_all_pages(driver, wait, input_url, filename):

    current_page = input_url

    max_pages = 12
    page_count = 0

    while page_count < max_pages:

        driver.get(current_page)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.e-10tu4d6'))
        )

        products = driver.find_elements(By.CSS_SELECTOR, 'div.e-10tu4d6 div a')

        products_links = [
            p.get_attribute("href")
            for p in products
            if p.get_attribute("href")
        ]

        print(f"\nFound {len(products_links)} products")

        scrape_products(driver, wait, products_links, filename)

        page_count += 1

        print(f"Page {page_count} completed\n")

        try:

            pages = driver.find_elements(By.CSS_SELECTOR, 'div.e-awidgz nav a')

            next_page = pages[-1].get_attribute('href')

            if not next_page or next_page == current_page:
                print("No more pages")
                break

            current_page = next_page

        except:

            print("Pagination ended")

            break


# ----------------------------
# Initialize browser
# ----------------------------
def initiate_browser():

    driver = webdriver.Chrome()

    wait = WebDriverWait(driver, 15)

    input_url = input("Enter URL: ")

    category_name = input("Enter category name: ")

    filename = f"{category_name}.csv"

    return driver, wait, input_url, filename


# ----------------------------
# Main
# ----------------------------
def main():

    driver, wait, input_url, filename = initiate_browser()

    get_all_pages(driver, wait, input_url, filename)

    print("\nScraping completed successfully")

    driver.quit()


if __name__ == "__main__":
    main()