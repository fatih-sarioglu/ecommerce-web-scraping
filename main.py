from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
import requests
import random
import time
import json
import os

# below are for switching between test and release modes
########################################################
# if you are testing and don't want the code run for too long,
# you make the testing True and you can adjust the COMMENTS_UPPER_LIMIT and PRODUCTS_UPPER_LIMIT to a small number
# the code will scrape 10 products' data and their 10 comments
# if you want to run on release mode (as it is asked in the case study), you just make the testing False
testing = True
COMMENTS_UPPER_LIMIT = 10
PRODUCTS_UPPER_LIMIT = 10

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
    #time.sleep(2)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()

    # accept the cookies
    #driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
    time.sleep(2)

    # hover over electronics tab and click computers
    electronics = driver.find_element(By.XPATH, '//*[@id="navigation-wrapper"]/nav/ul/li[8]/a')
    computers = driver.find_element(By.XPATH, '//*[@id="sub-nav-5"]/div/div/div[5]/div/ul/li[1]/a')

    actions = ActionChains(driver=driver)
    actions.move_to_element(electronics).perform()
    time.sleep(0.2)
    actions.move_to_element(computers).click().perform()
    # time.sleep(2)

    # click laptops option
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sticky-aggregations"]/div/div[1]/div[2]/div/div/div[1]/div/a'))).click()

    # click laptops option
    # driver.find_element(By.XPATH, '//*[@id="sticky-aggregations"]/div/div[1]/div[2]/div/div/div[1]/div/a').click()
    # time.sleep(2)

    return driver

# this functions gets links of all the laptops that have more than 100 reviews and puts them into a list 
def get_product_links(driver):
    # start with sorting products
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/div/div'))).click()
    #driver.find_element(By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/div/div').click()
    #time.sleep(0.1)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/ul/li[7]/span'))).click()
    #driver.find_element(By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/ul/li[7]/span').click()
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
            time.sleep(random.uniform(1.1, 1.5))

    return links, driver

# this functions gets to the each product's page and scrapes the data of each of them
def get_product_data(product_links, driver): # , driver

    product_data = []
    product_id = 0

    random.shuffle(product_links)

    os.mkdir('Output')
    os.mkdir('Output\\Product_Photos')

    for link in product_links:
        # random wait for undetectability
        if((product_id + 1) % 20 == 0):
            wait = wait = random.uniform(10, 15)
        # else:
        #     wait = random.uniform(2, 4)  
        # time.sleep(wait)

        # get to the product page
        driver.get(link)

        # already done in first function, delete after testing
        #driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
        #time.sleep(3)

        product = {'id': product_id}

        # num questions, num favs, prod title, price
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'pr-new-br')))
        h1 = driver.find_element(By.CLASS_NAME, 'pr-new-br')
        product['title'] = h1.find_element(By.XPATH, './/a').get_attribute('innerHTML') + " " + h1.find_element(By.XPATH, './/span').get_attribute('innerHTML')
        
        product['numberOfQuestions'] = int(driver.find_element(By.CLASS_NAME, 'answered-questions-count').get_attribute('innerHTML')) # typecast to int
        product['numberOfFavs'] = int(driver.find_element(By.CLASS_NAME, 'favorite-count').get_attribute('innerHTML')) # typecast to int
        price = driver.find_element(By.CLASS_NAME, 'product-price-container').find_element(By.CLASS_NAME, 'prc-dsc').get_attribute('innerHTML')[:-3]
        product['price'] = int(price.replace('.', ''))

        # seller info
        seller_info_parent = driver.find_element(By.CLASS_NAME, 'widget-title.product-seller-line')
        seller_name = seller_info_parent.find_element(By.XPATH, './/div/div/div[1]/a').get_attribute('innerHTML')
        seller_rating = seller_info_parent.find_element(By.CLASS_NAME, 'sl-pn').get_attribute('innerHTML')

        product['sellerInfo'] = {
            'sellerName': seller_name,
            'sellerRating': float(seller_rating)
        }

        # product photos uploaded by the seller are scraped here
        next_button = driver.find_element(By.CLASS_NAME, 'gallery-icon-container.right')
        image_parent = driver.find_element(By.CLASS_NAME, 'base-product-image')

        image_sources = []
        image_id = 0

        os.mkdir(f'Output\\Product_Photos\\product_{product_id}')
        os.mkdir(f'Output\\Product_Photos\\product_{product_id}\\Seller_Photos')

        product['photos'] = []

        actions = ActionChains(driver=driver)
        actions.move_to_element(next_button).perform()

        while (True):
            time.sleep(random.uniform(0.2, 0.4))
            # if it's a video then pass this element
            if (image_parent.find_element(By.XPATH, './/div').get_attribute('class') != 'gallery-video-container'):
                # terminates the loop if it comes the the first photo again
                src = image_parent.find_element(By.XPATH, './/div/img').get_attribute('src')
                if(src in image_sources):
                    break

                image_sources.append(src)

                path = f"Output\\Product_Photos\\product_{product_id}\\Seller_Photos\\image_{image_id}.jpg"
                with open(path, 'wb') as f:
                    img = requests.get(src)
                    f.write(img.content)
                
                product['photos'].append(path)

                image_id += 1

            next_button.click()
        
        # comment data is scraped below
        ###############################

        # go to reviews page
        driver.find_element(By.CLASS_NAME, 'rvw-cnt-tx').click()
        time.sleep(random.uniform(1.5, 2))

        product['overallRating'] = float(driver.find_element(By.CLASS_NAME, 'ps-ratings__count-text').get_attribute('innerHTML'))
        num_comments = driver.find_element(By.XPATH,
                                        '//*[@id="rating-and-review-app"]/div/div/div/div[1]/div/div[2]/div[2]/div[3]/div').get_attribute('innerHTML')
        product['numberOfComments'] = int(num_comments[:num_comments.find(' ')])
        
        stars = driver.find_elements(By.CLASS_NAME, 'ps-stars__content')
        stars = stars[::-1]

        product['numberOfRatings'] = {}

        for star, element in enumerate(stars, 1):
            product['numberOfRatings'][f'{star}-star'] = int(element.find_element(By.XPATH, './/span').get_attribute('innerHTML')[1:-1])

        # get the comment data for 1 and 5-star comments
        product['comments'] = {
                '1StarComments': {},
                '5StarComments': {}
            }
        
        # make directory for comment photos
        os.mkdir(f'Output\\Product_Photos\\product_{product_id}\\Comment_Photos')

        comment_id = 0
        for i in [0, 4]:
            comments = []

            actions = ActionChains(driver=driver)

            driver.execute_script("arguments[0].click();", stars[i])
            time.sleep(random.uniform(1, 1.7))

            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'comment')))

            keep_scrolling = True
            while keep_scrolling:
                batch = driver.find_elements(By.CLASS_NAME, 'comment')

                if (len(batch) > len(comments)):
                    for element in batch[len(comments):]:
                        comment = {'commentId':  comment_id}                        

                        # click read more if comment is long
                        try:
                            read_more_button = element.find_element(By.CLASS_NAME, 'i-dropdown-arrow')
                            driver.execute_script("arguments[0].click();", read_more_button)
                            time.sleep(0.2)

                            content = driver.find_elements(By.CLASS_NAME, 'comment')[batch.index(element)].find_element(By.TAG_NAME, 'p').get_attribute('innerHTML')
                        except NoSuchElementException:
                            content = element.find_element(By.CLASS_NAME, 'comment-text').find_element(By.TAG_NAME, 'p').get_attribute('innerHTML')

                        # save the comment text
                        comments.append(content)
                        comment['content'] = content

                        # get the number of thumbs up
                        num_thumbs_up = int(element.find_element(By.CLASS_NAME, 'tooltip-main').find_element(By.TAG_NAME, 'span').get_attribute('innerHTML')[1:-1])
                        comment['numberOfThumbsUp'] = num_thumbs_up

                        # images that are uploaded by the customers are scraped here
                        small_images = element.find_elements(By.CLASS_NAME, 'item.review-image')

                        if (len(small_images) > 0):
                            os.mkdir(f'Output\\Product_Photos\\product_{product_id}\\Comment_Photos\\comment_{comment_id}')
                            comment['photos'] = []

                            actions.move_to_element(small_images[0]).click().perform()
                            time.sleep(random.uniform(0.8, 1))

                            for j in range(len(small_images)):
                                image_parent = driver.find_element(By.CLASS_NAME, 'react-transform-component.transform-component-module_content__uCDPE ')
                                next_button = driver.find_element(By.CLASS_NAME, 'arrow.next')
                                src = image_parent.find_element(By.XPATH, './/img').get_attribute('src')

                                comment_photo_path = f'Output\\Product_Photos\\product_{product_id}\\Comment_Photos\\comment_{comment_id}\\image_{j}.jpg'
                                with open(comment_photo_path, 'wb') as f:
                                    img = requests.get(src)
                                    f.write(img.content)
                                
                                comment['photos'].append(comment_photo_path)

                                # if there are more photos from this comment, click next otherwise close the photo displayer
                                if (j != len(small_images)-1):
                                    actions.move_to_element(next_button).click().perform()
                                    time.sleep(random.uniform(0.3, 0.6))
                                else:
                                    driver.find_element(By.CLASS_NAME, 'ty-modal-content.ty-relative.modal-class').find_element(By.TAG_NAME, 'a').click()
                                    time.sleep(random.uniform(0.1, 0.15))
                        
                        product['comments'][f'{i+1}StarComments'][f'comment_{comment_id}'] = comment
                        comment_id += 1

                        # if it reached to a certain number of comments stop scrolling
                        limit = COMMENTS_UPPER_LIMIT if testing else 100
                        if (len(comments) == product['numberOfRatings'][f'{i+1}-star'] or len(comments) == limit):
                            keep_scrolling = False
                            break
                
                # keep scrolling for new comments to appear
                if (keep_scrolling):
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                    time.sleep(1.5)

            # switch between filtering for 1-star and 5-star comments
            driver.execute_script("arguments[0].click();", stars[i])
            time.sleep(random.uniform(0.8, 1.1))

        # after scraping this particular product, add the dict to the list and increase the product_id for next prod
        product_data.append(product)
        product_id += 1

    return product_data

# this function outputs data to a .jsonl file
def to_jsonl(data):
    file = open('Output\\data.jsonl', 'w', encoding='utf-8')
    for product in data:
        json.dump(product, file, ensure_ascii=False)
        file.write('\n')

    file.close()
    return

# test
#########################################
# service = Service(executable_path='chromedriver.exe')
# driver = webdriver.Chrome(service=service)

# links = ['https://www.trendyol.com/huawei/matebook-d15-i5-1155g7-islemci-8gb-ram-512gb-ssd-15-6-inc-win-11-laptop-mistik-gumus-p-654281247?boutiqueId=61&merchantId=514600']

# scraped_data = get_product_data(links, driver)

# to_jsonl(scraped_data)

# execute the functions
#########################################
driver = get_to_the_page()

links, driver = get_product_links(driver)

# in the test version, you run for less amount of products and comments so it takes less time
scraped_data = None
if (testing):
    scraped_data = get_product_data(links[:PRODUCTS_UPPER_LIMIT], driver)
else:
    scraped_data = get_product_data(links, driver)

to_jsonl(scraped_data)