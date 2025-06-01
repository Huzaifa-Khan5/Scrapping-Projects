from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

def scrape_products(): 
    scraped_data=[]
    name=driver.find_element(by=By.CSS_SELECTOR,value='div.sr-resultTitle_ZySr1 h1').text
    j=1
    while True:
        try:
            products=driver.find_elements(by=By.XPATH,value='//*[@id="productcategory"]/main/div[2]/div/div/div/section/div[2]/div[2]/div/div')
            details_list=[]
            images=[]
            for i in range(len(products)):
                products=driver.find_elements(by=By.XPATH,value='//*[@id="productcategory"]/main/div[2]/div/div/div/section/div[2]/div[2]/div/div')
                products[i].click()
                driver.find_element(by=By.ID,value='datasheet-expand').click()
                img_links=driver.find_element(by=By.XPATH,value='//*[@id="datasheet"]/div[1]/img')
                # print(img_links.get_attribute('src'))
                images.append(img_links.get_attribute('src'))
                product_details=driver.find_elements(by=By.CSS_SELECTOR,value='table tbody tr td')
                details={}
                for k in range(0, len(product_details), 2):
                    details[product_details[k].text]=product_details[k+1].text
                    
                details_list.append(details)
                driver.back()
                # time.sleep(2)
                
            prod_names=driver.find_elements(by=By.CSS_SELECTOR,value='div.sr-productSummary__title_f5flP')
            prod_prices=driver.find_elements(By.CSS_SELECTOR,value='div.sr-detailedPriceInfo__price_sYVmx')
            print(len(prod_names),len(prod_prices),len(images),len(details_list))
            for prod_name,prod_price,img_link,prod_detail in zip(prod_names,prod_prices,images,details_list):
                scraped_data.append({"Product Name":prod_name.text,"Price":prod_price.text[2:],"Product Image":img_link,**prod_detail})
            
            print(j)
            page=driver.find_element(by=By.CSS_SELECTOR,value='div.sr-pagination_geD74 a.sr-pageArrow_HufQY')
            driver.get(page.get_attribute('href'))
            j+=1
            
        except:
            break
    
    return scraped_data,name




def initiate_browser():
    driver=webdriver.Chrome()
    driver.maximize_window()
    return driver


def get_url():
    input_url=input("Enter URL: ")
    driver.get(input_url)
    time.sleep(10)
    # wait = WebDriverWait(driver,60)
    shadow_host = driver.find_element(by=By.ID, value="usercentrics-cmp-ui")
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
    footer = shadow_root.find_element(By.CSS_SELECTOR, "footer.center")
    button=footer.find_element(by=By.ID ,value="deny")
    button.click()



def main():
    global driver
    driver=initiate_browser()
    get_url()
    data,name=scrape_products()
    df = pd.DataFrame(data)
    df.to_csv(f"{name}.csv", index=False)
    driver.quit()

if __name__ == '__main__':
    main()