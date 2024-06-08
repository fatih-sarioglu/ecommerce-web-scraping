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
# if you want to run on release mode (as it is asked in the case study: 100 products and 100 comments), you just make the testing False
testing = False
PRODUCTS_UPPER_LIMIT = 5
COMMENTS_UPPER_LIMIT = 3

# this function goes to trendyol.com and navigates to the laptops page and returns the driver to be used in another function
def get_to_the_page():
    url = "https://www.trendyol.com"

    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    # get the page
    driver.get(url)

    # accept the cookies
    wait = WebDriverWait(driver, 30)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
    accept_button = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
    driver.execute_script("arguments[0].click();", accept_button)
    #time.sleep(2)

    # hover over electronics tab and click computers
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="navigation-wrapper"]/nav/ul/li[8]/a')))
    electronics = driver.find_element(By.XPATH, '//*[@id="navigation-wrapper"]/nav/ul/li[8]/a')
    computers = driver.find_element(By.XPATH, '//*[@id="sub-nav-5"]/div/div/div[5]/div/ul/li[1]/a')

    actions = ActionChains(driver=driver)
    actions.move_to_element(electronics).perform()
    time.sleep(random.uniform(1, 1.5))
    actions.move_to_element(computers).click().perform()

    # click laptops option
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="sticky-aggregations"]/div/div[1]/div[2]/div/div/div[1]/div/a')))
    laptops = driver.find_element(By.XPATH, '//*[@id="sticky-aggregations"]/div/div[1]/div[2]/div/div/div[1]/div/a')
    driver.execute_script("arguments[0].click();", laptops)

    return driver

# this functions gets links of all the laptops that have more than 100 reviews and puts them into a list 
def get_product_links(driver):
    # start with sorting products
    wait = WebDriverWait(driver, 30)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/div/div')))
    open_list = driver.find_element(By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/div/div')
    driver.execute_script("arguments[0].click();", open_list)
    time.sleep(random.uniform(0.2, 0.4))
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/ul/li[7]/span')))
    most_rated = driver.find_element(By.XPATH, '//*[@id="search-app"]/div/div[1]/div[2]/div[1]/div[2]/div/ul/li[7]/span')
    driver.execute_script("arguments[0].click();", most_rated)
    time.sleep(random.uniform(1, 1.5))

    links = []

    keep_scrolling = True

    while (keep_scrolling):
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'p-card-wrppr.with-campaign-view')))
        batch = driver.find_elements(By.CLASS_NAME, 'p-card-wrppr.with-campaign-view')

        # this condition checks if new elements appeared after scrolling down
        if (len(batch) > len(links)):

            for element in batch[len(links):]:
                try:
                    rating_count = int(element.find_element(By.CLASS_NAME, 'ratingCount').get_attribute('innerHTML')[1:-1])
                except:
                    time.sleep(60)
                
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

    random.shuffle(links)
    with open('product_links.txt', 'w', encoding='utf-8') as f:
        for link in links:
            f.write(link + ',')

    return links, driver

# this functions gets to the each product's page and scrapes the data of each of them
def get_product_data(product_links, driver): # , driver

    wait = WebDriverWait(driver, 30)

    #product_data = []
    product_id = 0

    #random.shuffle(product_links)

    os.mkdir('Output')
    os.mkdir('Output\\Product_Photos')

    for link in product_links:
        file = open('Output\\data.jsonl', 'a', encoding='utf-8')

        print(link)
        # random wait for undetectability
        if((product_id + 1) % 8 == 0):
            time.sleep(random.uniform(14, 22))

        # get to the product page
        driver.get(link)

        product = {'id': product_id}

        # num questions, num favs, prod title, price
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pr-new-br')))
        h1 = driver.find_element(By.CLASS_NAME, 'pr-new-br')
        product['title'] = h1.find_element(By.XPATH, './/a').get_attribute('innerHTML') + " " + h1.find_element(By.XPATH, './/span').get_attribute('innerHTML')
        
        product['numberOfQuestions'] = int(driver.find_element(By.CLASS_NAME, 'answered-questions-count').get_attribute('innerHTML')) # typecast to int
        product['numberOfFavs'] = int(driver.find_element(By.CLASS_NAME, 'favorite-count').get_attribute('innerHTML')) # typecast to int
        price = driver.find_element(By.CLASS_NAME, 'product-price-container').find_element(By.CLASS_NAME, 'prc-dsc').get_attribute('innerHTML')[:-3]
        price = price.replace('.', '')
        product['price'] = float(price.replace(',', '.'))

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

                path = f"Product_Photos\\product_{product_id}\\Seller_Photos\\image_{image_id}.jpg"
                with open(f"Output\\{path}", 'wb') as f:
                    img = requests.get(src)
                    f.write(img.content)
                
                product['photos'].append(path)

                image_id += 1

            #next_button.click()
            wait.until(EC.element_to_be_clickable((next_button)))
            driver.execute_script("arguments[0].click();", next_button)
        
        # comment data is scraped below
        ###############################

        # go to reviews page
        # driver.find_element(By.CLASS_NAME, 'rvw-cnt-tx').click()
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'rvw-cnt-tx')))
        reviews = driver.find_element(By.CLASS_NAME, 'rvw-cnt-tx')
        driver.execute_script("arguments[0].click();", reviews)
        time.sleep(random.uniform(1, 1.5))

        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ps-ratings__count-text')))
        product['overallRating'] = float(driver.find_element(By.CLASS_NAME, 'ps-ratings__count-text').get_attribute('innerHTML'))
        num_comments = driver.find_element(By.XPATH,
                                        '//*[@id="rating-and-review-app"]/div/div/div/div[1]/div/div[2]/div[2]/div[3]/div').get_attribute('innerHTML')
        product['numberOfComments'] = int(num_comments[:num_comments.find(' ')])
        
        stars = driver.find_elements(By.CLASS_NAME, 'ps-stars__content')
        stars = stars[::-1]

        product['numberOfRatings'] = {}

        product['numberOfRatings']['5-star'] = int(stars[len(stars)-1].find_element(By.XPATH, './/span').get_attribute('innerHTML')[1:-1])
        decrease = 0
        for star, element in enumerate(stars[len(stars)-2: 0:-1], 4):
            product['numberOfRatings'][f'{star-decrease}-star'] = int(element.find_element(By.XPATH, './/span').get_attribute('innerHTML')[1:-1])
            decrease += 2
        product['numberOfRatings']['1-star'] = int(stars[0].find_element(By.XPATH, './/span').get_attribute('innerHTML')[1:-1])

        # get the comment data for 1 and 5-star comments
        product['comments'] = {
                '1StarComments': {},
                '5StarComments': {}
            }
        
        # make directory for comment photos
        os.mkdir(f'Output\\Product_Photos\\product_{product_id}\\Comment_Photos')

        comment_id = 0
        one_star_idx, five_stars_idx = 0, (len(stars)-1)
        for i in [one_star_idx, five_stars_idx]:
            comments = []

            #actions = ActionChains(driver=driver)
            wait.until(EC.element_to_be_clickable((stars[i])))
            driver.execute_script("arguments[0].click();", stars[i])
            time.sleep(random.uniform(1, 1.7))

            wait.until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'comment')))

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

                            #actions.move_to_element(small_images[0]).click().perform()
                            driver.execute_script("arguments[0].click();", small_images[0])
                            

                            for j in range(len(small_images)):
                                time.sleep(random.uniform(1, 1.5))
                                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'react-transform-component.transform-component-module_content__uCDPE')))
                                image_parent = driver.find_element(By.CLASS_NAME, 'react-transform-component.transform-component-module_content__uCDPE')
                                image = image_parent.find_element(By.XPATH, './/img')
                                src = image.get_attribute('src')

                                comment_photo_path = f'Product_Photos\\product_{product_id}\\Comment_Photos\\comment_{comment_id}\\image_{j}.jpg'
                                with open(f'Output\\{comment_photo_path}', 'wb') as f:
                                    img = requests.get(src)
                                    f.write(img.content)
                                
                                comment['photos'].append(comment_photo_path)

                                next_button = driver.find_element(By.CLASS_NAME, 'arrow.next')
                                # if there are more photos from this comment, click next otherwise close the photo displayer
                                if (j != len(small_images)-1):
                                    wait.until(EC.element_to_be_clickable((next_button)))
                                    driver.execute_script("arguments[0].click();", next_button)
                                    time.sleep(random.uniform(0.1, 0.3))
                                else:
                                    close_photo = driver.find_element(By.CLASS_NAME, 'ty-modal-content.ty-relative.modal-class').find_element(By.TAG_NAME, 'a')
                                    wait.until(EC.element_to_be_clickable(close_photo))
                                    driver.execute_script("arguments[0].click();", close_photo)
                                    time.sleep(random.uniform(0.1, 0.15))
                        
                        # if it reached to a certain number of comments stop scrolling
                        limit = COMMENTS_UPPER_LIMIT if testing else 100

                        if (i == one_star_idx):
                            product['comments']['1StarComments'][f'comment_{comment_id}'] = comment
                            comment_id += 1
                            if (len(comments) == product['numberOfRatings']['1-star'] or len(comments) == limit):
                                keep_scrolling = False
                                break
                        else:
                            product['comments']['5StarComments'][f'comment_{comment_id}'] = comment
                            comment_id += 1
                            if (len(comments) == product['numberOfRatings']['5-star'] or len(comments) == limit):
                                keep_scrolling = False
                                break                        
                
                # keep scrolling for new comments to appear
                if (keep_scrolling):
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                    time.sleep(1.5)

            # switch between filtering for 1-star and 5-star comments
            driver.execute_script("arguments[0].click();", stars[i])
            time.sleep(random.uniform(0.8, 1.1))

        # after scraping that particular product, add the dict to the list and increase the product_id for next prod
        #product_data.append(product)
        json.dump(product, file, ensure_ascii=False)
        file.write('\n')
        file.close()
        product_id += 1

    return #product_data

# execute the functions
#########################################
driver = get_to_the_page()
links = None

# if product links are already scraped, do not scrape again
# read the links from the file and move on with scraping product data
if (os.path.isfile('product_links.txt')):
    with open('product_links.txt', 'r', encoding='utf-8') as file:
        content = file.read()
        links = content.split(sep=',')
else:
    links, driver = get_product_links(driver)

# in testing, scrape less products
if (testing):
    get_product_data(links[:PRODUCTS_UPPER_LIMIT], driver)
else:
    get_product_data(links, driver)