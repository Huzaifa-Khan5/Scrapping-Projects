from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

def scrape_products(wait):
    name=driver.find_element(by=By.CSS_SELECTOR,value='h1.e-l195ut').text
    data=[]
    pages=driver.find_elements(by=By.CSS_SELECTOR,value='div.e-awidgz ul li a')
    page_links=[]
    for page_no in range(len(pages)):
        if page_no<=5:
            if pages[page_no].get_attribute('href')!=None:
                # print(pages[page_no].get_attribute('href'))
                page_links.append(pages[page_no].get_attribute('href'))

    for page_link in page_links:
        print(page_link)
        driver.get(page_link)
        products=driver.find_elements(by=By.CSS_SELECTOR,value='div.e-10tu4d6 div a')
        products_links=[product.get_attribute("href") for product in products]
        for j,product_link in enumerate(products_links):
            driver.get(product_link)
            time.sleep(4)
            prod_name=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'h1.e-3x90er'))).text
            try:
                discount_price=driver.find_element(by=By.ID,value='sale_price').text
                original_price=driver.find_element(by=By.CSS_SELECTOR,value='span.e-4jky3p').text
            except NoSuchElementException:
                original_price=driver.find_element(by=By.CSS_SELECTOR,value='div.e-dzwvfb').text
                discount_price=None
    
            images=driver.find_elements(by=By.CSS_SELECTOR,value='div.e-2szg1 div picture img')
            img_links=[]
            for i,img in enumerate(images):
                if i<4:
                    img_links.append(img.get_attribute('srcset').split(',')[-1])
        
        
            details={}
            about=driver.find_elements(by=By.CSS_SELECTOR,value='div.e-hctwcp div')
            for i in range(len(about)):
                a=(about[i].text.split('\n'))
                details[(a[0])]=','.join(a[1:])

            print(j)

            data.append({'Name':prod_name,
                         'Discounted Price':discount_price,
                         'Original Price':original_price,
                         "Images":','.join(img_links),
                         **details})
            
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
    driver.quit()

if __name__ == '__main__':
    main()