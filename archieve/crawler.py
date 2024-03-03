from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from urllib.parse import urlparse, urlunparse
import csv

def parse_url(url: str) -> str:

    parsed_url = urlparse(url)
    if not parsed_url.scheme :
        if not parsed_url.netloc :
            updated_url = parsed_url._replace(scheme='https', netloc=parsed_url.path, path='', query='', params='', fragment='')
        else :
            updated_url = parsed_url._replace(scheme='https', query='', params='', fragment='')
    else :
        updated_url = parsed_url._replace(query='', params='', fragment='')
    print(updated_url)
    return updated_url.geturl()

if __name__=="__main__":

    dd = pd.read_csv("university.csv")

    cleaned_urls_1 = list(set(url.strip() for url in list(dd['홈페이지'])))
    cleaned_urls_1.append('https://poticket.interpark.com')
    cleaned_urls_1.append('https://ticket.melon.com')
    cleaned_urls_1.append('http://ticket.yes24.com')
    cleaned_urls_1.append('www.ticketlink.co.kr')
    cleaned_urls_1.append('http://browse.auction.co.kr')


    cleaned_urls = [parse_url(x) for x in cleaned_urls_1]

    print(cleaned_urls)


    csv_file_path = '../url_list.csv'

    # CSV 파일로 저장
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for url in cleaned_urls:
            csv_writer.writerow([url])


if __name__=="__main__":
    print(parse_url("http://www.cku.ac.kr/cku/index.do"))