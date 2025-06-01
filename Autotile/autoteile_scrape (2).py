from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

def scrape_products(input_url):
    j=1
    scraped_data=[]
    name=driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[1]/div/div[1]/h1').text
    while True:
        if j>1:
            page_url='?filter=1&page='+str(j)
        else:
            page_url='?filter=1'
            
        driver.get(input_url+page_url)
         
        products=driver.find_elements(by=By.XPATH,value='/html/body/div[3]/div[2]/div[4]/div[1]/div[2]/div/div')
        products=(products[1:])
        if len(products)>0:
            for i in range(len(products)):
                products=driver.find_elements(by=By.XPATH,value='/html/body/div[3]/div[2]/div[4]/div[1]/div[2]/div/div')
                products=(products[1:])
                
                products[i].click()
                    
                prod_name=driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[1]/div[2]/section/h1').text
                try:
                    prod_img=driver.find_element(by=By.CSS_SELECTOR,value='div.carousel-inner div span img').get_attribute('src')
                except NoSuchElementException:
                    prod_img=None
                product_price=driver.find_element(by=By.XPATH,value='/html/body/div[3]/div[1]/div/section/div[1]/div[2]/div[1]/div[1]/div[2]/span').text
                details_key=driver.find_elements(by=By.XPATH,value='/html/body/div[3]/div[1]/div[2]/section/dl/dt')
                details_value=driver.find_elements(by=By.XPATH,value='/html/body/div[3]/div[1]/div[2]/section/dl/dd')
                details={}
                for detail_key,detail_value in zip(details_key,details_value):
                    details[detail_key.text]=detail_value.text
                scraped_data.append({"Product Name":prod_name,"Product Image":prod_img,"Price":product_price,**details})
                driver.back()
                time.sleep(2) 
            j+=1
        else:
            break
    return scraped_data,name
           

def initiate_browser():
    driver=webdriver.Chrome()
    return driver

def get_url():
    input_url=input("Enter URL: ")
    driver.get(input_url)
    wait = WebDriverWait(driver,60)
    wait.until(
    EC.visibility_of_element_located((By.XPATH,'//*[@id="cookieconsent"]/div/div/div[3]/a[1]'))).click()
    return input_url

def main():
    global driver
    driver=initiate_browser()
    input_url=get_url()
    data,name=scrape_products(input_url)
    df = pd.DataFrame(data)
    df.to_csv(f"{name}.csv", index=False)
    driver.quit()

if __name__ == '__main__':
    main()