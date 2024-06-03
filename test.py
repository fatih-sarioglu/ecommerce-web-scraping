from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import requests
import random
import time
import json
import os

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)

link = 'https://www.trendyol.com/huawei/matebook-d15-i5-1155g7-islemci-8gb-ram-512gb-ssd-15-6-inc-win-11-laptop-mistik-gumus-p-654281247/yorumlar?boutiqueId=61&merchantId=514600'

driver.get(link)
time.sleep(2)

# already done in first function, delete after testing
driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
time.sleep(3)

stars = driver.find_elements(By.CLASS_NAME, 'ps-stars__content')
stars = stars[::-1]

product = {}

for star, element in enumerate(stars, 1):
    product[f'{star}-star'] = int(element.find_element(By.XPATH, './/span').get_attribute('innerHTML')[1:-1])

print(product)


# get the comment data for 1 and 5-star comments
for i in [4]:
    comments = []
    comment_id = 0

    actions = ActionChains(driver=driver)

    driver.execute_script("arguments[0].click();", stars[i])

    time.sleep(2)

    keep_scrolling = True

    comments = []

    while keep_scrolling:

        batch = driver.find_elements(By.CLASS_NAME, 'comment')

        if (len(batch) > len(comments)):
            for element in batch[len(comments):]:
                # click read more if comment is long
                try:
                    read_more_button = element.find_element(By.CLASS_NAME, 'i-dropdown-arrow')
                    driver.execute_script("arguments[0].click();", read_more_button)
                    time.sleep(0.2)

                    content = driver.find_elements(By.CLASS_NAME, 'comment')[batch.index(element)].find_element(By.TAG_NAME, 'p').get_attribute('innerHTML')
                except NoSuchElementException:
                    content = element.find_element(By.CLASS_NAME, 'comment-text').find_element(By.TAG_NAME, 'p').get_attribute('innerHTML')

                comments.append(content)
                print(content)

                num_thumbs_up = int(element.find_element(By.CLASS_NAME, 'tooltip-main').find_element(By.TAG_NAME, 'span').get_attribute('innerHTML')[1:-1])
                print(num_thumbs_up)

                small_images = element.find_elements(By.CLASS_NAME, 'item.review-image')

                if (small_images):
                    actions.move_to_element(small_images[0]).click().perform()
                    time.sleep(1)

                    for j in range(len(small_images)):
                        image_parent = driver.find_element(By.CLASS_NAME, 'react-transform-component.transform-component-module_content__uCDPE ')
                        next_button = driver.find_element(By.CLASS_NAME, 'arrow.next')
                        src = image_parent.find_element(By.XPATH, './/img').get_attribute('src')

                        with open(f'image{comment_id}-{j}.jpg', 'wb') as f:
                            img = requests.get(src)
                            f.write(img.content)

                        if (j != len(small_images)-1):
                            actions.move_to_element(next_button).click().perform()
                            time.sleep(random.uniform(0.5, 0.9))
                        else:
                            driver.find_element(By.CLASS_NAME, 'ty-modal-content.ty-relative.modal-class').find_element(By.TAG_NAME, 'a').click()
                            time.sleep(0.3)
                
                comment_id += 1

                if (len(comments) == product[f'{i+1}-star'] or len(comments) == 20):
                    keep_scrolling = False
                    print('yo')
                    break

        if (keep_scrolling):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

    driver.execute_script("arguments[0].click();", stars[i])

    print(len(comments))

    time.sleep(1)