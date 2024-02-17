"""
Logic 1.f
    return 150 url does not exists

    return url 가장 가까운 시간
"""
from repository import URLRepository, MySQLRepository
import re
from fastapi import HTTPException
import requests
import logging
from datetime import datetime, timedelta

urlrepository = URLRepository('url_list.csv')
mysqlrepository = MySQLRepository()
logging.basicConfig(level=logging.INFO)

def get_correction_from_db(url: str, es) -> int:
    global urlrepository
    global mysqlrepository

    if es is None:
        if urlrepository.exists(url):
            logging.info(f"Case 1 {url}")
            return mysqlrepository.get_elasped_time(url)
        logging.info(f"Case 2 {url}")
        return 150

    if urlrepository.exists(url):
        logging.info(f"Case 3 {url}")
        return (mysqlrepository.get_elasped_time(url) + int(es)) / 2

    logging.info(f"Case 4 {url}")
    return int(es)


def parse_url(url: str) -> str:
    logging.info(url)
    url = re.sub(r'^www\.', '', url)
    logging.info(url)
    ## url = re.sub(r'\/.*', '', url)
    url = url.replace("https://", "").replace("http://","")
    logging.info(url)
    return url


def get_server_time_from_url(url: str):
    try:
        response = requests.get(url)

        server_datetime = datetime.strptime(response.headers['Date'], "%a, %d %b %Y %H:%M:%S %Z")
        server_timestamp = server_datetime.timestamp() * 1000
        return server_timestamp

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_server_time_from_url_by_string(url: str):
    try:
        response = requests.get(url)
        server_date = response.headers['Date']
        server_datetime = datetime.strptime(server_date, "%a, %d %b %Y %H:%M:%S %Z")
        server_time_string = server_datetime.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
        return server_time_string

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))