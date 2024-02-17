from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import csv

if __name__=="__main__":
    dd = pd.read_csv("university.csv")

    cleaned_urls_1 = list(set(url.strip() for url in list(dd['홈페이지'])))
    cleaned_urls = [x.replace("http://", "").replace("https://", "") for x in cleaned_urls_1]


    cleaned_urls.append('https://poticket.interpark.com/')
    cleaned_urls.append('https://ticket.melon.com/')
    cleaned_urls.append('http://ticket.yes24.com/')
    cleaned_urls.append('www.ticketlink.co.kr')
    cleaned_urls.append('http://browse.auction.co.kr/')


    print(cleaned_urls)

    csv_file_path = '../url_list.csv'

    # CSV 파일로 저장
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for url in cleaned_urls:
            csv_writer.writerow([url])