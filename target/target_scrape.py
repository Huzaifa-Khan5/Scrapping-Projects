from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

def scrape_products(wait):
    name=driver.find_element(by=By.CSS_SELECTOR,value='div [aria-label="Breadcrumbs"] ol li span').text
    data=[]
    wait.until(
    EC.element_to_be_clickable((By.XPATH,'//*[@id="pageBodyContainer"]/div/div[1]/div/div/div[4]/div/div/div[1]/div[3]/div/div/div'))).click()
    li=driver.find_elements(by=By.CSS_SELECTOR,value='ul.Options_styles_options__TK_Sd li')
    number_of_pages=len(li)
    j=1
    while j<number_of_pages:
       
        scroll_pause_time=1.5
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
        max_retries=3
        failed_urls = []
        products=driver.find_elements(by=By.CSS_SELECTOR,value='[data-test="product-details"] div div div [data-test="product-title"]')
        print(len(products))
        
        products_links=[i.get_attribute('href') for i in products]
        for k,product_link in enumerate(products_links):
            for attempt in range(max_retries):
                try:
                    driver.set_page_load_timeout(30)  # Set page load timeout
                    driver.get(product_link)
                    product_name=wait.until(
        EC.presence_of_element_located((By.ID,'pdp-product-title-id'))).text
                    product_price=wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'[data-test="product-price"]'))).text
                    break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for URL: {product_link}")
                    if attempt == max_retries - 1:
                        print(f"Failed to load product after {max_retries} attempts")
                        failed_urls.append(product_link)
                    driver.refresh()
                                
            wait.until(
        EC.visibility_of_element_located((By.XPATH,'//*[@id="product-detail-tabs"]/div/div[3]/button'))).click()
            details=driver.find_elements(by=By.CSS_SELECTOR,value='[data-test="item-details-specifications"] div')
            product_details={}
            try:
                for detail in details:
                    key,value=(detail.text.split(":"))
                    product_details[key]=value
            except:
                pass
                
            img_urls=[]
            images=driver.find_elements(by=By.CSS_SELECTOR,value='[data-test="@web/SiteTopOfFunnel/BaseStackedImageGallery"] div div div div div div img')
            for img_no,image in enumerate(images):
                if img_no>=4:
                    pass
                img_urls.append(image.get_attribute('src'))
                try:
                    img=",".join(img_urls)
                except:
                    pass
        
            data.append({"Product Name":product_name,"Product Price":product_price,"Images":img,**product_details})
            print(f"succesfully scraped product No:{k}")
            driver.back()
            time.sleep(3)
                
        try:
            driver.find_element(by=By.XPATH,value='//*[@id="pageBodyContainer"]/div/div[1]/div/div/div[4]/div/div/div[1]/div[3]/div/div/div').click()
            li=driver.find_elements(by=By.CSS_SELECTOR,value='ul.Options_styles_options__TK_Sd li')
            (li[j].click())
            print(j)
            j+=1
        except:                
            break
        
        # return data,name
    return data,name



def initiate_browser():
    driver=webdriver.Chrome()
    return driver

def get_url():
    input_url=input("Enter URL: ")
    driver.get(input_url)
    driver.maximize_window()
    driver.refresh()
    wait = WebDriverWait(driver,60)
    return wait


def main():
    global driver
    driver=initiate_browser()
    wait=get_url()
    data,name=scrape_products(wait)
    df = pd.DataFrame(data)
    df.to_csv(f"{name}.csv", index=False)
    driver.quit()

if __name__ == '__main__':
    main()