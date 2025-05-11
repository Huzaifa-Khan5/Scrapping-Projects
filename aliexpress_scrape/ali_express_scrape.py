from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from selenium.webdriver.common.keys import Keys


def scrape_products():
    products=driver.find_elements(by=By.CSS_SELECTOR,value='div.hm_hn div div div a')
    print(len(products))
    products_links=[product.get_attribute("href") for product in products if product.get_attribute("href").startswith("https://www.aliexpress.com/item")]
    print(len(products_links))
    data=[]
    for prod_link in products_links:
        driver.get(prod_link)
        
        name=driver.find_element(by=By.CSS_SELECTOR,value='div.title--wrap--UUHae_g [data-pl="product-title"]').text

        price=driver.find_element(by=By.CSS_SELECTOR,value='[data-pl="product-price"] div span').text

        imgs=driver.find_elements(by=By.CSS_SELECTOR,value='div div.slider--item--RpyeewA div img')
        img_links=[img_link.get_attribute('src') for i,img_link in enumerate(imgs) if i<5 and img_link.get_attribute('src') is not None]
        
    #     try:
    #         driver.find_element(by=By.XPATH,value='//*[@id="nav-specification"]/button').click()
    #     except:
    #         pass
    #     details={}
    #     keys=driver.find_elements(by=By.CSS_SELECTOR,value='ul.specification--list--GZuXzRX li div div.specification--title--SfH3sA8')
    #     values=driver.find_elements(by=By.CSS_SELECTOR,value='ul.specification--list--GZuXzRX li div div.specification--desc--Dxx6W0W')

    #     for key,value in zip(keys,values):
    #         details[key.text]=value.text
    data.append({"Name":name,"Price":price,"Images":','.join(img_links)})
    
def go_to_page(input_url):
    product_data=[]
    for page_no in range(1,9):
        if page_no==1:
            get_url(input_url)
            scroll_page()
            print("1")
            prod_data=scrape_products()
            product_data.append(prod_data)
        else:
            get_url(input_url)
            scroll_page()
            page=driver.find_element(by=By.XPATH,value='//*[@id="root"]/div[1]/div/div/div[2]/ul/li[10]/div/input')
            # //*[@id="root"]/div[1]/div/div/div[2]/ul/li[12]/div/input
            page.send_keys(page_no)
            page.send_keys(Keys.ENTER)
            print(page_no)
            prod_data=scrape_products()
            product_data.append(prod_data)
            
    data = sum(product_data, [])

    return data
def initiate_browser():
    driver=webdriver.Chrome()
    return driver
def get_url(input_url):
    driver.get(input_url)
    try:
        driver.maximize_window()
    except: 
        pass


def select_usd_prices():
    wait=WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="_full_container_header_23_"]/div[2]/div/div[2]/div[2]/div/div'))).click()
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="_full_container_header_23_"]/div[2]/div/div[2]/div[2]/div[2]/div[6]/div/div[1]'))).click()
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="_full_container_header_23_"]/div[2]/div/div[2]/div[2]/div[2]/div[6]/div/div[2]/div[3]'))).click()
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="_full_container_header_23_"]/div[2]/div/div[2]/div[2]/div[2]/div[7]'))).click()
def scroll_page():
    scroll_pause_time=2
    scroll_step=300
    last_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    while True:
                # Scroll down a small amount
        current_position = min(current_position + scroll_step, last_height)
        driver.execute_script(f"window.scrollTo(0, {current_position});")
                    
                    # Wait for new content to load
        time.sleep(scroll_pause_time)
                    
                    # Calculate new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
                    
                    # Break if we've reached the bottom
        if current_position >= last_height:
                        # One final check for any dynamically loaded content
            time.sleep(scroll_pause_time * 2)
            final_height = driver.execute_script("return document.body.scrollHeight")
            if final_height == last_height:
                break
            last_height = final_height
def main():
    global driver
    driver=initiate_browser()
    input_url=input("Enter URL: ")
    get_url(input_url)
    select_usd_prices()
    time.sleep(5)
    go_to_page(input_url)
    # df = pd.DataFrame(data)
    # df.to_csv(f"{name}.csv", index=False)
    driver.quit()


if __name__ == "__main__":
    main()
