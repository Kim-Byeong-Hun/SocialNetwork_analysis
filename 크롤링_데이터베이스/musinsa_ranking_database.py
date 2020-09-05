from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd
import urllib.request
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
from datetime import datetime

# 현재시간
now = datetime.now()

# 크롬 전체화면으로 키기
#options = Options()
#options.add_argument('--kiosk')
#driver = webdriver.Chrome("C:/Users/user/chromedriver/chromedriver.exe", chrome_options=options)

driver = webdriver.Chrome("C:/Users/user/chromedriver/chromedriver.exe")

# 무신사 url 입력
driver.get("https://store.musinsa.com/app/contents/bestranking")
# waiting
driver.implicitly_wait(10)


now_date = str(now.date()) + '-' + str(now.hour)
page = 1

while page <= 2:
    if not os.path.isdir('D:/musinsa_store/'):
        os.mkdir('D:/musinsa_store/')
    csvFile = open('D:/musinsa_store/musinsa_ranking_data.csv','a',newline='')
    writer = csv.writer(csvFile)
    #if(page==1):
        #writer.writerow(('날짜','사이트 링크','이미지 링크', '브랜드명', '가격', '랭킹'))
        #writer.writerow(('date','rank', 'brand', 'price'))
    
    # 1~2페이지 변경
    pages = page+2
    driver.find_element_by_xpath('//*[@id="product_list"]/div[2]/div[5]/div/div/a[%s]' %pages).send_keys(Keys.ENTER)
    
    # img 로드될때까지 waiting
    #element = WebDriverWait(driver, 10).until(
        #EC.presence_of_element_located((By.CSS_SELECTOR, 'img[src^="//image.msscdn.net/images/goods_img/"]'))
    #)
    
    # 페이지 스크롤 다운
    target = 1000
    while True:
        now_height = driver.execute_script("return window.pageYOffset;")
        driver.execute_script("window.scrollTo(300, {0});".format(target))
        time.sleep(2)
        target = target + 1000
        new_height = driver.execute_script("return window.pageYOffset;")
        if now_height == new_height:
            break
    
    items = driver.find_element_by_id("searchList")
    #urls = []
    #for i in range(0,90):
        #urls += items.find_elements_by_css_selector('li:nth-child(%s) > div.li_inner > div.list_img > a' %(i+1))
    #images = items.find_elements_by_css_selector('img[src^="//image.msscdn.net/images/goods_img/"]')
    brands = driver.find_elements_by_xpath('//*[@id="searchList"]/li/div[2]/div[2]/p[1]/a')
    prices = items.find_elements_by_class_name('price')
    ranks = items.find_elements_by_xpath('//*[@id="searchList"]/li/p')
    # hearts = items.find_elements_by_class_name('txt_cnt_like')
    
    try:
        #urls_l = []
        # image_urls = []
        brand_l = []
        price_l = []
        rank_l = []
        # heart_l = []
        result = []

        #for index, url in enumerate(urls):
            #urls_l.append(url.get_attribute("href"))
        #for image in images:
            #image_urls.append(image.get_attribute("src"))
        for brand in brands:
            brand_l.append(brand.text)
        for price in prices:
            price_list = price.text.split("\n")
            if len(price_list)==3:
                price_l.append(price_list[1])
            else:
                price_l.append(price_list[0])
        for rank in ranks:
            rank_l.append(rank.text)
        #for heart in hearts:
            #heart_l.append(heart.text)
        
        for x in range(0, len(brand_l)):
            result.append(now_date)
            #result.append(urls_l[x])
            result.append(rank_l[x])
            #result.append(image_urls[x])
            result.append(brand_l[x])
            result.append(price_l[x])
            # result.append(heart_l[x])
        
        for y in range(0, len(result),4):
            writer.writerow(result[y:y+4])
        
        #for index, image_url in enumerate(image_urls):
            # imgdir = 'D:/musinsa_store/musinsa_img/%s/%s/' % (page, now_date)
            # if not os.path.isdir(imgdir):
                # os.mkdir(imgdir)
            #urllib.request.urlretrieve(image_url, imgdir + brand_l[index] + rank_l[index] + ".jpg")
        
    finally:
        csvFile.close()
        
    page += 1
    time.sleep(5)

driver.close()

