from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from selenium.webdriver.common.keys import Keys

def scrape_products(wait):
    data=[]
    name=driver.find_element(by=By.XPATH,value='//*[@id="breadcrumb"]/ul/li[3]/dl/dt/a').text
    
    while True:
        try:
            products=driver.find_elements(by=By.CSS_SELECTOR,value="div.container-right div div a")
            products_links=[product.get_attribute("href") for product in products]
        
            for i,product_link in enumerate(products_links): 
                driver.get(product_link)
                try:
                    product_name=driver.find_element(by=By.CSS_SELECTOR,value="div.widget.prod-info-title h1").text
                except:
                    product_name=driver.find_element(by=By.CSS_SELECTOR,value="span.title-text").text
                
                price=driver.find_element(by=By.CSS_SELECTOR,value="strong[itemprop='price']").text
                    
                highlights=driver.find_element(by=By.CSS_SELECTOR,value='div div.description-container div').text
                details={}
                list_to_extract=highlights.split("\n")
                details[list_to_extract[0]]=list_to_extract[1:]
                
                product_colors=driver.find_elements(by=By.CSS_SELECTOR,value='''li.sku-attr-container.attr-v-show-li.is-color.is-sku-img.attr-model 
                div div.attr-item-container div.clearfix span''')
                
                for color in product_colors:
                    try:
                        wait.until(EC.element_to_be_clickable((color))).click()
                    except:
                        pass
                    
                    time.sleep(2)
                    color_name=driver.find_element(by=By.CSS_SELECTOR,value='''li.sku-attr-container.attr-v-show-li.is-color.is-sku-img.attr-model
                    div.attr-v-show.attr-v-model.form-item h5 div.attr-value''').text
                    
                    images=driver.find_elements(by=By.CSS_SELECTOR,value="div.pull-left.litb-span30 div div.left.carousel_img_wrapper div div ul li span img")
                    image_urls=[img.get_attribute("src") for i,img in enumerate(images) if i<4]
                    row = {
                            "Product Name": product_name,
                            "Price": price,
                            "Color": color_name,
                            "Image URLs": ",".join(image_urls),
                            **details
                        }
                data.append(row)
                driver.back()
                print(i) 
            try:
                page=driver.find_element(by=By.CSS_SELECTOR,value="li.next a")
                driver.get(page.get_attribute("href"))
            except:
                break    
        except:
            continue
    
    return data,name           

def initiate_browser():
    driver=webdriver.Chrome()
    return driver

def get_url():
    input_url=input("Enter URL: ")
    driver.get(input_url)
    driver.maximize_window()
    wait=WebDriverWait(driver, 15)
    return wait

def main():
    global driver
    driver=initiate_browser()
    wait=get_url()
    data,name=scrape_products(wait)
    df = pd.DataFrame(data)
    df.to_csv(f"{name}.csv", index=False)
    # driver.quit()

if __name__ == '__main__':
    main()
