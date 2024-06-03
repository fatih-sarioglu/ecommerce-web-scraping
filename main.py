from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver import ActionChains
import requests
import random
import time
import json
import os

# service = Service(executable_path='chromedriver.exe')
# driver = webdriver.Chrome(service=service)

# this function goes to trendyol.com and navigates to the laptops page and returns the driver to be used in another function
def get_to_the_page():

    url = "https://www.trendyol.com"

    # create driver
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    # get the page
    driver.get(url)

    # accept the cookies
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()

    # hover over electronics tab and click computers
    time.sleep(3)
    electronics = driver.find_element(By.XPATH, '//*[@id="navigation-wrapper"]/nav/ul/li[8]/a')
    computers = driver.find_element(By.XPATH, '//*[@id="sub-nav-5"]/div/div/div[5]/div/ul/li[1]/a')

    actions = ActionChains(driver=driver)
    actions.move_to_element(electronics).perform()
    time.sleep(2)
    actions.move_to_element(computers).click().perform()

    # click laptops option
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="sticky-aggregations"]/div/div[1]/div[2]/div/div/div[1]/div/a').click()

    time.sleep(3)
    # driver.quit()

    return driver

# this functions gets links of all the laptops that have more than 100 reviews and puts them into a list 
def get_product_links(driver):
    # start with sorting products
    driver.find_element(By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/div/div').click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/ul/li[7]/span').click()
    time.sleep(1.5)

    links = []

    keep_scrolling = True

    while (keep_scrolling):
        
        batch = driver.find_elements(By.CLASS_NAME, 'p-card-wrppr.with-campaign-view')

        # this condition checks if new elements appeared after scrolling down
        if (len(batch) > len(links)):

            for element in batch[len(links):]:
                rating_count = int(element.find_element(By.CLASS_NAME, 'ratingCount').get_attribute('innerHTML')[1:-1])
                print(rating_count)
                if (rating_count > 100):
                    # if the elements has more than 100 reviews, add it to the links
                    links.append(element.find_element(By.XPATH, './/div[1]/a').get_attribute('href'))
                
                else:
                    # otherwise, do not add the element and end the loop
                    keep_scrolling = False
                    break
        
        # scroll down for new elements to appear
        if (keep_scrolling):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
                        

    return [links, driver]

def get_product_data(product_links, driver): # , driver

    product_data = []
    product_id = 0

    random.shuffle(product_links)

    os.mkdir('Product_Photos')

    for link in product_links:
        # random wait for undetectability
        if((product_id + 1) % 20 == 0):
            wait = wait = random.uniform(8, 15)
        else:
            wait = random.uniform(2, 4)  
        time.sleep(wait)

        driver.get(link)
        time.sleep(2)

        # already done in first function, delete after testing
        driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
        time.sleep(3)

        product = {'id': product_id}

        # num_q, num_fav, prod_title, price, seller_info, photos
        h1 = driver.find_element(By.CLASS_NAME, 'pr-new-br')
        product['title'] = h1.find_element(By.XPATH, './/a').get_attribute('innerHTML') + " " + h1.find_element(By.XPATH, './/span').get_attribute('innerHTML')
        
        product['numberOfQuestions'] = driver.find_element(By.CLASS_NAME, 'answered-questions-count').get_attribute('innerHTML') # typecast to int
        product['numberOfFavs'] = driver.find_element(By.CLASS_NAME, 'favorite-count').get_attribute('innerHTML') # typecast to int
        price = driver.find_element(By.CLASS_NAME, 'product-price-container').find_element(By.CLASS_NAME, 'prc-dsc').get_attribute('innerHTML')[:-3]
        product['price'] = price.replace('.', '')

        # seller info
        seller_info_parent = driver.find_element(By.CLASS_NAME, 'widget-title.product-seller-line')
        seller_name = seller_info_parent.find_element(By.XPATH, './/div/div/div[1]/a').get_attribute('innerHTML')
        seller_rating = seller_info_parent.find_element(By.CLASS_NAME, 'sl-pn').get_attribute('innerHTML')

        product['sellerInfo'] = {
            'sellerName': seller_name,
            'sellerRating': seller_rating,
        }

        # product photos
        next_button = driver.find_element(By.CLASS_NAME, 'gallery-icon-container.right')
        image_parent = driver.find_element(By.CLASS_NAME, 'base-product-image')

        image_sources = []
        image_id = 0

        os.mkdir(f'Product_Photos\\{product_id}')

        product['photos'] = {}

        actions = ActionChains(driver=driver)
        actions.move_to_element(next_button).perform()

        while (True):
            time.sleep(random.uniform(0.3, 0.5))
            # if it's a video then pass this element
            if (image_parent.find_element(By.XPATH, './/div').get_attribute('class') != 'gallery-video-container'):
                # terminates the loop if it comes the the first photo again
                src = image_parent.find_element(By.XPATH, './/div/img').get_attribute('src')
                if(src in image_sources):
                    break

                image_sources.append(src)

                path = f"Product_Photos\\{product_id}\\{image_id}.jpg"
                with open(path, 'wb') as f:
                    img = requests.get(src)
                    f.write(img.content)
                
                product['photos'][f'image{image_id}'] = path

                image_id += 1

            next_button.click()
            

        # overall_rating, num_each_rating, num_comments
        # 5 and 1 star comments' content, thumbs_up, photos (max 100 from each rating)



        product_data.append(product)
        product_id += 1

        print(product_data[0])

        

    return

def to_jsonl():
    return

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)

links = ['https://www.trendyol.com/acer/aspire3-intel-celeron-n4500-4gb-128gb-ssd-dos-15-6-gumus-dizustu-bilgisayar-acer-turkiye-garantili-p-656066934']

get_product_data(links, driver)