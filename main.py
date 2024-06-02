import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver import ActionChains
import time

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)

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

def get_product_data(product_links): # , driver

    product_data = []

    for link in product_links:
        driver.get(link)

        product = {}

        # num_q, num_fav, prod_title, price, seller_info, photos
        h1 = driver.find_element(By.CLASS_NAME, 'pr-new-br')
        title = h1.find_element(By.XPATH, './/a').get_attribute('innerHTML') + " " + h1.find_element(By.XPATH, './/span').get_attribute('innerHTML')
        
        num_q = driver.find_element(By.CLASS_NAME, 'answered-questions-count').get_attribute('innerHTML') # typecast to int
        num_fav = driver.find_element(By.CLASS_NAME, 'favorite-count').get_attribute('innerHTML') # typecast to int
        price = driver.find_element(By.CLASS_NAME, 'product-price-container').find_element(By.XPATH, './/div/div/div/div[2]/span').get_attribute('innerHTML')[:-3]
        price_refined = price.replace('.', '')

        seller_info_parent = driver.find_element(By.CLASS_NAME, 'seller-widget.widget')
        seller_name = seller_info_parent.find_element(By.XPATH, './/[1][1]/div[1]/a').get_attribute('innerHTML')
        seller_rating = seller_info_parent.find_element(By.XPATH, './/[1][1]/div[3]').get_attribute('innerHTML')
        seller_follower_count = seller_info_parent.find_element(By.XPATH, './/[1][2]').get_attribute('innerHTML')
        seller_follower_count_refined = seller_follower_count.replace('Takipçi', '')

        



        # overall_rating, num_each_rating, num_comments
        # 5 and 1 star comments' content, thumbs_up, photos (max 100 from each rating)




    return

def to_jsonl():
    return

driver = get_to_the_page()
links, driver_new = get_product_links(driver=driver)

print(links)