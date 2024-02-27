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
import time

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
    url = url.replace("https://", "").replace("http://", "")
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


def get_server_time(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            server_time = response.headers['Date']
            elasped_time = response.elapsed.total_seconds()
            return elasped_time, server_time
        else:
            print("Failed to retrieve server time. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def estimate_millisecond_discrepancy(url, num_requests=10):
    previous_second = None
    for _ in range(num_requests):
        elasped_time, server_time = get_server_time(url)
        print(f"process time {elasped_time} {server_time}")

        if server_time is not None:
            # Extract the second part from the server time
            current_second = int(server_time.split(' ')[-2][-2:])
            # Check if the second part has changed
            if previous_second is not None and current_second != previous_second:
                if elasped_time < 0.2 :
                    milliseconds = int(time.time() * 1000)
                    print(f"Second changed: {previous_second} -> {current_second}, Milliseconds: {milliseconds}")
                    print(convert_to_timestamp(server_time, elasped_time))
                    return convert_to_timestamp(server_time, elasped_time)

            previous_second = current_second

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


def convert_to_timestamp(date_string, milliseconds):
    date_object = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    date_object = date_object.replace(microsecond=int(milliseconds * 1000000))
    timestamp = int(date_object.timestamp()*1000)

    return timestamp


if __name__ == "__main__":
    url = "http://www.interpark.com"

    print(estimate_millisecond_discrepancy(url, num_requests=20))