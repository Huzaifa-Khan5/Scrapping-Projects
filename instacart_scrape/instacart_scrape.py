from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

def scrape_products(wait,products_links):
    # name=driver.find_element(by=By.CSS_SELECTOR,value='h1.e-l195ut').text
    data=[]
        
    for j,product_link in enumerate(products_links):
        driver.get(product_link)
        time.sleep(4)
        name=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'h1.e-vbt7pb'))).text
        
        try:
            price=wait.until(EC.presence_of_element_located((By.ID,'sale_price'))).text
        # original_price=driver.find_element(by=By.CSS_SELECTOR,value='span.e-4jky3p').text
        except:
            try:
                price=wait.until(EC.presence_of_element_located((By.ID,'regular_price'))).text
            except:
                try:
                    price=wait.until(EC.presence_of_element_located((By.CSS_SELECTOT,'div.e-175s8ne'))).text
                except:
                    price=''
        
        images=driver.find_elements(by=By.CSS_SELECTOR,value='div.e-2szg1 div picture img')
        img_links=[]
        for i,img in enumerate(images):
            if i<4:
                img_links.append(img.get_attribute('srcset').split(',')[-1])
            
            
        details={}
        about=driver.find_element(by=By.CSS_SELECTOR,value='div.e-b8kzem')
        # for i in range(len(about)):
        a=(about.text.split('\n'))
        details[(a[0])]=','.join(a[1:])
    
        print(j)

        data.append({'Name':name,'Price':price,"Images":','.join(img_links),**details})
            
    return data

def get_page(wait,input_url):
    all_data = []
    previous_page=input_url
    while True:
        driver.get(previous_page)
        products=driver.find_elements(by=By.CSS_SELECTOR,value='div.e-10tu4d6 div a')
        products_links=[product.get_attribute("href") for product in products]

        page_data = scrape_products(wait,products_links)
        all_data.extend(page_data)

        driver.get(previous_page)
        pages=driver.find_elements(by=By.CSS_SELECTOR,value='div.e-awidgz nav a')
    # print(pages[-1].get_attribute('href')) 
        # print("previous page",previous_page)
        next_page=pages[-1].get_attribute('href')
        # print("next page",next_page)
        if next_page == previous_page:
            break
        driver.get(next_page)    
        previous_page=next_page

    return all_data


def initiate_browser():
    driver=webdriver.Chrome()
    input_url=input("Enter URL: ")
    category_name=input("Enter category name: ")
    wait=WebDriverWait(driver, 15)
    return driver,wait,input_url,category_name
    

def main():
    global driver
    driver,wait,input_url,category_name=initiate_browser()
    all_data=get_page(wait,input_url)
    df = pd.DataFrame(all_data)
    df.to_csv(f"{category_name}.csv", index=False)
    driver.quit()

if __name__ == '__main__':
    main()