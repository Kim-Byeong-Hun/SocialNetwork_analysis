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
import re
from urllib.request import urlopen
from datetime import datetime
from random import *
import pymysql


# 현재 날짜정보 추출
now = datetime.now()
now_day = now.day
now_year = now.year
now_month = now.month

db = pymysql.connect(host='localhost', user="root", password='qudgns5129', db='musinsa_database')
curs = db.cursor()


driver = webdriver.Chrome("C:/Users/user/chromedriver/chromedriver.exe")

# styling url의 기본 구조 저장
styling_basic_url = 'https://store.musinsa.com/app/styles/views/%s?sex=%s&use_yn_360=&style_type=&brand=&model=&max_rt=2020&min_rt=2010&year_date=%s&month_date=%s&display_cnt=60&list_kind=small&sort=view_cnt&page=1'

for sex in range(1,3):
    sex *= 2
    # 2020년까지만 크롤링 할 것이기 때문에 다음년도 고려 X
    if now_day == 1:
        driver.get("https://store.musinsa.com/app/styles/lists?sex=%s&use_yn_360=&style_type=&brand=&model=&max_rt=2020&min_rt=2010&year_date=%s&month_date=%s&display_cnt=60&list_kind=small&sort=view_cnt&page=1" %(sex,year,(now_month - 1)))
        driver.set_window_size(1600, 1024)
        
        # 디렉토리 없을 시 생성하기
        if not os.path.isdir('D:/musinsa_store/'):
            os.mkdir('D:/musinsa_store/')
        
        # 남자 - 여자 따로 csv파일에 저장
        if(sex == 2):
            csvFile_1 = open('D:/musinsa_store/musinsa_styling_data_man.csv','a',newline='')
            csvFile_2 = open('D:/musinsa_store/musinsa_styling_relation_man.csv','a',newline='')
            writer1 = csv.writer(csvFile_1)
            writer2 = csv.writer(csvFile_2)
        else:
            csvFile_1 = open('D:/musinsa_store/musinsa_styling_data_woman.csv','a',newline='')
            csvFile_2 = open('D:/musinsa_store/musinsa_styling_relation_woman.csv','a',newline='')
            writer1 = csv.writer(csvFile_1)
            writer2 = csv.writer(csvFile_2)
        
        # 페이지 스크롤 다운(이미지 로드 안되는 문제 최소화)
        target = 1000
        while True:
            now_height = driver.execute_script("return window.pageYOffset;")
            driver.execute_script("window.scrollTo(300, {0});".format(target))
            time.sleep(3)
            target = target + 1000
            new_height = driver.execute_script("return window.pageYOffset;")
            if now_height == new_height:
                break
        
        # 에러 최소화
        try:
            # 전체 데이터 저장할 리스트
            result = []
            
            # 릴레이션 테이블 저장할 리스트
            table_result = []
            
            # 셀레니움 사용
            images = [] 
            urls = []
            styling_ids = []
            comment_n = []
            style_name = []
            view_n = []
            model_name = []

            for i in range(0,60):
                image_xpath = driver.find_elements_by_xpath('//*[@id="catelist"]/div[6]/div/div[3]/ul/li[%s]/div/div[1]/a/img' %(i+1))
                image_src = image_xpath[0].get_attribute('src')
                images.append(image_src)
            for i in range(0,60):
                path = driver.find_elements_by_xpath('//*[@id="catelist"]/div[6]/div/div[3]/ul/li[%s]/div/div[1]/a' %(i+1))
                element = path[0].get_attribute('onclick')
                styling_id = re.findall("\d+",element)
                # id도 따로 저장
                styling_ids.append(styling_id[0])
                # 포맷팅으로 기본 styling_url에 
                urls.append(styling_basic_url %(styling_id[0],sex,year,month))
            for i in range(0, 60):
                comment_n_xpath = driver.find_elements_by_xpath('//*[@id="catelist"]/div[6]/div/div[3]/ul/li[%s]/div/div[2]/p[1]/span[2]' %(i+1))
                # 2017년도에 xpath가 누락된 경우 존재, 이를 해결하기 위해 if문 사용
                if not comment_n_xpath:
                    comment_n.append('0')
                else:
                    comment_n.append(comment_n_xpath[0].text)
            for i in range(0,60):
                style_xpath = driver.find_elements_by_xpath('//*[@id="catelist"]/div[6]/div/div[3]/ul/li[%s]/div/div[2]/p[2]' %(i+1))
                style_text = style_xpath[0].text
                style_name.append(style_text)
            for i in range(0,60):
                view_xpath = driver.find_elements_by_xpath('//*[@id="catelist"]/div[6]/div/div[3]/ul/li[%s]/div/div[2]/p[3]' %(i+1))
                view_text = view_xpath[0].text
                view_text_slice = view_text[8:]
                view_n.append(view_text_slice)
            for i in range(0,60):
                model_xpath = driver.find_elements_by_xpath('//*[@id="catelist"]/div[6]/div/div[3]/ul/li[%s]/div/div[2]/p[4]' %(i+1))
                model_text = model_xpath[0].text
                model_name.append(model_text[5:])


            # BeautifulSoup 사용
            brand_list = []
            price_list = []
            content_list = []
            price_lists_result = []
                
            for i in range(0,60):
                url = urls[i]
                html = urlopen(url)
                bsObject = BeautifulSoup(html, "html.parser")

                brand_a = bsObject.find_all('a', {"class":'brand'})
                price_div = bsObject.find_all('div', {"class":'price'})
                content_p = bsObject.find_all('p',{'class':'styling_cnt'})
                    
                # 한 링크 당 하나의 리스트로 저장함(상품이 몇개 있을 지 모르기 때문)
                brand_result = []
                price_result = []

                for brand in brand_a:
                    brand_result.append(brand.text)
                for price in price_div:
                    text = price.text.strip('\t\n').split('\n')
                    price_result.append(text)
                for content in content_p:
                    text = ''.join(content.text.splitlines()).lstrip(' ')
                    content_list.append(text)
                    
                # price_list안에 '%' 포함된 거 삭제 - 세일정보는 불필요하다고 생각해서 제거
                for index, x in enumerate(price_result):
                    for y in range(0, len(price_result[index])):
                        if('%' in price_result[index][y]):
                            del price_result[index][y]
                    
                brand_list.append(brand_result)
                price_list.append(price_result)
                    
            # 세일정보 없앤 price데이터 저장
            for x in range(0, 60):
                price_lists = []
                for y in range(0, len(price_list[x])):
                    price_lists += price_list[x][y]
                price_lists_result.append(price_lists)
                
                        
            # 데이터 날짜('일'부분은 불필요하다 느껴서 28일로 통일)
            now_date = str(now_year) + '-' + str(now_month - 1) + '28'
                
            # 최종 데이터 저장        
            for x in range(0, 60):
                result.append(now_date)
                result.append(urls[x])
                result.append(styling_ids[x]) # 외래키
                result.append(comment_n[x])
                result.append(style_name[x])
                result.append(view_n[x])
                result.append(model_name[x])
                result.append(content_list[x])
                        
            for y in range(0, len(result),8):
                writer1.writerow(result[y:y+8])
                query = """INSERT IGNORE INTO musinsa_styling VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
                curs.execute(query,(result[y+0],result[y+1],result[y+2],int(result[y+3]),result[y+4], int(result[y+5].replace(',','')),result[y+6],result[y+7]))
                db.commit()
                    
            # 테이블 데이터 저장 (price_list 칼럼은 int형이기 때문에 replace)
            for x in range(0, 60):
                for y in range(0, len(price_lists_result[x])):
                    table_result.append(styling_ids[x]) # 외래키
                    table_result.append(brand_list[x][y])
                    table_result.append(price_lists_result[x][y].replace(',',"").replace("원",""))
                
            for y in range(0, len(table_result),3):
                writer2.writerow(table_result[y:y+3])
                query = """INSERT IGNORE INTO musinsa_styling_relation VALUES(%s, %s, %s);"""
                curs.execute(query,(table_result[y+0],table_result[y+1],int(table_result[y+2])))
                db.commit()
                    
                    
            # 이미지 파일 저장
            for index, image in enumerate(images):
                imgdir = 'D:/musinsa_store/musinsa_img/%s/%s/%s/' % (sex, now_year, (now_month-1))
                if not os.path.isdir(imgdir):
                    os.mkdir(imgdir)
                urllib.request.urlretrieve(image, imgdir + view_n[index] + '_' + product_ids[index] + ".jpg")

                    
        finally:
            csvFile_1.close()
            csvFile_2.close()
            
        time.sleep(3)

# db 닫기            
db.close()

