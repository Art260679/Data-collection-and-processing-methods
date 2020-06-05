""""
Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import json

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome('/home/art/HW_Selenium/chromedriver', options=chrome_options)

client = MongoClient('localhost', 27017)
db = client['mvideo']
collection = db.mvideo

driver.get('https://www.mvideo.ru/')

region = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, "(//a[@class='next-btn sel-hits-button-next'])[2]")))

actions = ActionChains(driver)
actions.move_to_element(region).click().perform()

while True:
    try:
        button = driver.find_element_by_class_name('next-btn sel-hits-button-next')
    except Exception:
        break
    actions.move_to_element(button).click().perform()

hit = driver.find_elements_by_class_name('sel-hits-block')[1]
products = hit.find_elements_by_class_name('gallery-list-item')

for product in products:
    hits = json.loads(product.find_element_by_tag_name('a').get_attribute('data-product-info').replace('\n', ''))
    hits['_id'] = hits['productId']
    hits['link'] = product.find_element_by_tag_name('a').get_attribute('href')
    collection.update_one({'_id': hits['_id']}, {'$set': hits}, upsert=True)

driver.quit()
