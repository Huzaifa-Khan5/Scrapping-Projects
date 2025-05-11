from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from flask import Flask,request,render_template,flash
from selenium.webdriver.chrome.options import Options


app = Flask(__name__)
app.secret_key = 'the random string'

def scrape_products(): 
    scraped_data=[]
    name=driver.find_element(by=By.CSS_SELECTOR,value='div.sr-resultTitle_ZySr1 h1').text
    j=1
    while True:
        try:
            products=driver.find_elements(by=By.CSS_SELECTOR,value='[data-testid="resultList"] div div [data-testid="resultItemLink"] a')
            product_links=[product.get_attribute('href') for product in products]
            details_list=[]
            images=[]
            for product_link in product_links:
                driver.get(product_link)
                try:
                    driver.find_element(by=By.ID,value='datasheet-expand').click()
                except:
                    pass
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

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        input_url = request.form['url']
        if input_url:
            if input_url.startswith("http://") or input_url.startswith("https://"):
                get_url(input_url)
            else: 
                flash('Please enter a valid URL', 'danger')
        else:
            flash('Please enter a URL', 'danger')
    return render_template('index.html')

def get_url(input_url):
    global driver
    print(input_url)
    driver=initiate_browser()    
    driver.get(input_url)
    time.sleep(10)
    # wait = WebDriverWait(driver,60)
    shadow_host = driver.find_element(by=By.ID, value="usercentrics-cmp-ui")
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
    footer = shadow_root.find_element(By.CSS_SELECTOR, "footer.center")
    button=footer.find_element(by=By.ID ,value="deny")
    button.click()

    data,name=scrape_products()
    df = pd.DataFrame(data)
    df.to_csv(f"{name}.csv", index=False)
    driver.quit()
    
    
    

if __name__ == '__main__':
    app.run(debug=True)