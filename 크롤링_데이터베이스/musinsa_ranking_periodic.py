import pymysql
import csv
import re

db = pymysql.connect(host='localhost', user="root", password='qudgns5129', db='musinsa_database')
curs = db.cursor()

try:
    with open('D:\musinsa_store\musinsa_ranking_data.csv') as file:
        ranking_data = []
        for line in file.readlines():
            ranking_data.append(line.split(','))

    date = []
    rank = []
    brand = []
    price = []
    for i in range(0,len(ranking_data)-1):

        date.append(ranking_data[i+1][0])
        rank.append(ranking_data[i+1][1])
        brand.append(ranking_data[i+1][2])
        price.append(ranking_data[i+1][3] + ranking_data[i+1][4])

    for i in range(0,len(price)):
        price[i] = re.sub('[원\n\"]','',price[i])


    for i in range(0,len(rank)):
        rank[i] = re.sub('[\-\▲\▼"]','',rank[i])

    for i in range(0,len(rank)):
        rank[i] = rank[i].split("위")

    rank_result = []
    rank_change = []
    for i in range(0,len(rank)):
        rank_result.append(rank[i][0])
        rank_change.append(rank[i][1].replace(' ',''))

    for i in range(0,len(rank)):
        if rank_change[i]=="":
            rank_change[i] = '0'

    for i in range(0, len(date)):
        query = """INSERT IGNORE INTO musinsa_ranking VALUES(%s, %s, %s, %s, %s);"""
        curs.execute(query,(date[i][0:10],int(rank_result[i]),int(rank_change[i]),brand[i],int(price[i])))
        db.commit()

finally:
    db.close()




