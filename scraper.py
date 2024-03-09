import pandas as pd
import urllib3
import time
import statistics
import csv
import socket
import pymysql
from sqlalchemy import create_engine
from service import parse_url

from repository import MySQLRepository
from urllib.parse import urlparse, urlunparse


def parse_url_for_scrape(url: str) -> str:

    parsed_url = url.replace("http://", "").replace("https://", "")

    return parsed_url

def elasped_time_checker(host_list: list[str], http: urllib3.PoolManager, connection,
                         test_num: int = 10) -> pd.DataFrame:
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')

    for host in host_list:
        parsed_host = parse_url_for_scrape(host)

        elapsed_times = []
        status_codes = {}
        try:
            ip_address = socket.gethostbyname(parsed_host)
        except Exception as e:
            ip_address = "None"
            print(e)
        try:
            for i in range(test_num):
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                start_time = time.time()
                response = http.request('GET', host)
                end_time = time.time()

                elapsed_time = end_time - start_time
                elapsed_times.append(elapsed_time)

                status_code = response.status
                status_codes[status_code] = status_codes.get(status_code, 0) + 1

            # statistics
            average_time = statistics.mean(elapsed_times)
            median_time = statistics.median(elapsed_times)
            max_time = max(elapsed_times)
            min_time = min(elapsed_times)
            std_dev_time = statistics.stdev(elapsed_times) if len(elapsed_times) > 1 else 0

            print("\n=== Statistics ===")
            print(f"URL: {host}")
            print(f"IP Address: {ip_address}")
            print(f"Average Time: {average_time}")
            print(f"Median Time : {median_time}")
            print(f"Maximum Time: {max_time}")
            print(f"Minimum Time: {min_time}")
            print(f"Standard Deviation: {std_dev_time}")
            print(f"Status Codes: {status_codes}")

            # 결과 기록
            info = [current_time, host, average_time, median_time, min_time,
                    max_time, std_dev_time, ip_address]

            # if Failure over 80%
            if status_codes[200] < test_num * 0.8:
                raise Exception

            save_to_db(connection, info)

        except Exception as e:
            save_to_fail_log(connection, [current_time, host])
            print(f"Fail to scrape data \n {e}")



def get_db_connection():
    user = 'admin'
    password = 'fkdls3323'
    host = 'exit-database.c9heedqt7ayj.ap-northeast-2.rds.amazonaws.com'
    db_name = 'foryoutime'
    db_port = '3306'

    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 database=db_name,
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection


def get_db_sqlalchemy_connection():
    user = 'admin'
    password = 'fkdls3323'
    host = 'exit-database.c9heedqt7ayj.ap-northeast-2.rds.amazonaws.com'
    db_name = 'foryoutime'
    db_port = '3306'
    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    return engine

def save_to_db(connection, values):
    columns = ['checked_datetime', 'host', 'average_time', 'median_time', 'min_time', 'max_time', 'std_dev_time',
               'ip_address']
    try:
        with connection.cursor() as cursor:
            sql_insert = f"INSERT INTO checked_time ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
            cursor.execute(sql_insert, values)
        connection.commit()
    finally:
        print("Successfully insert")


def save_to_fail_log(connection, values):
    columns = ['checked_datetime', 'host']
    try:
        with connection.cursor() as cursor:
            sql_insert = f"INSERT INTO scrape_failure_log ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
            cursor.execute(sql_insert, values)
        connection.commit()
    finally:
        print("Successfully insert Log")


def calculate_grade(connection):
    try:
        # Calculate Grade
        with connection.cursor() as cursor:
            sql = 'SELECT host, average_time FROM checked_time'
            cursor.execute(sql)
            results = cursor.fetchall()

        df = pd.DataFrame(results)
        p50 = df.groupby('host')['average_time'].quantile(0.5)
        p75 = df.groupby('host')['average_time'].quantile(0.75)
        p90 = df.groupby('host')['average_time'].quantile(0.9)
        p95 = df.groupby('host')['average_time'].quantile(0.95)

        # Percentile 값을 DataFrame으로 저장
        percentile_df = pd.DataFrame({
            'A': p50,
            'B': p75,
            'C': p90,
            'D': p95
        })

        percentile_df.reset_index(inplace=True)
        percentile_df.rename(columns={'index': 'host'}, inplace=True)
        print(percentile_df)
        print(percentile_df.columns)

        engine = get_db_sqlalchemy_connection()
        with engine.connect() as conn, conn.begin():

            # DataFrame을 새로운 테이블로 생성합니다.
            percentile_df.to_sql(name="grade", con=conn, if_exists='replace')

    finally:
        print("Over")


if __name__ == "__main__":
    db_connection = get_db_connection()
    mysqlrepository = MySQLRepository()

    url_list = mysqlrepository.get_all_urls()
    http = urllib3.PoolManager()
    elasped_time_checker(url_list, http, db_connection)
    calculate_grade(db_connection)
    db_connection.close()
    mysqlrepository.close()