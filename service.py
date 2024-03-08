from repository import MySQLRepository
from fastapi import HTTPException
import requests
import logging
from datetime import datetime
import time
from urllib.parse import urlparse, urlunparse
from constant import Parameter

mysqlrepository = MySQLRepository()
logging.basicConfig(level=logging.INFO)


def get_correction_from_db(url: str, es) -> int:
    global mysqlrepository

    if es is None:
        if mysqlrepository.exists_url(url):
            logging.info(f"Case 1 {url}")
            return mysqlrepository.get_elasped_time(url)
        logging.info(f"Case 2 {url}")
        mysqlrepository.add_url(url)
        return 150

    if mysqlrepository.exists_url(url):
        logging.info(f"Case 3 {url}")
        return (mysqlrepository.get_elasped_time(url) + int(es)) / 2

    mysqlrepository.add_url(url)
    logging.info(f"Case 4 {url}")
    return int(es)


def parse_url(url: str) -> str:
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        updated_url = parsed_url._replace(scheme='https', netloc=parsed_url.path, path='', query='', params='', fragment='')
        print(updated_url)
    else:
        updated_url = parsed_url._replace(query='', params='', fragment='')
    return urlunparse(updated_url)


"""
  return_type : timestamp
  return_type : string
  return_type : korea_string
"""


def get_server_time_from_url(url: str, return_type):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            server_time = response.headers['Date']
            elasped_time = response.elapsed.total_seconds()
            if return_type == "string":
                return elasped_time, server_time

            elif return_type == "timestamp":
                server_datetime = datetime.strptime(server_time, "%a, %d %b %Y %H:%M:%S %Z")
                server_timestamp = server_datetime.timestamp() * 1000
                return server_timestamp

            elif return_type == "korea_string":
                server_datetime = datetime.strptime(server_time, "%a, %d %b %Y %H:%M:%S %Z")
                server_time_string = server_datetime.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
                return server_time_string
            else:
                raise Exception("wrong type")
        else:
            print("Failed to retrieve server time. Status code:", response.status_code)
            return None, None
    except Exception as e:
        print("An error occurred:", str(e))
        raise HTTPException(status_code=400, detail=str(e))


def estimate_millisecond_discrepancy(url, num_requests=Parameter.SYNC_ZERO_MILLI_TRIAL):
    previous_second = None
    for _ in range(num_requests):
        elasped_time, server_time = get_server_time_from_url(url, return_type="string")
        print(f"process time {elasped_time} {server_time}")

        if server_time is not None:
            # Extract the second part from the server time
            current_second = int(server_time.split(' ')[-2][-2:])
            # Check if the second part has changed
            if previous_second is not None and current_second != previous_second:
                if elasped_time < Parameter.SYNC_ZERO_MILLI_ERROR:
                    milliseconds = int(time.time() * 1000)
                    print(f"Second changed: {previous_second} -> {current_second}, Milliseconds: {milliseconds}")
                    print(convert_to_timestamp(server_time, elasped_time))
                    return convert_to_timestamp(server_time, elasped_time)

            previous_second = current_second
    ## if Fail to get estimate_millsecond
    raise HTTPException(500, "Fail to get estimated millisecond")


def convert_to_timestamp(date_string, milliseconds):
    date_object = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')
    date_object = date_object.replace(microsecond=int(milliseconds * 1000000))
    timestamp = int(date_object.timestamp() * 1000)

    return timestamp


if __name__ == "__main__":
    url = "http://www.interpark.com"

    print(parse_url(url))
    print(estimate_millisecond_discrepancy(url, num_requests=20))
