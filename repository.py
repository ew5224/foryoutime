from typing import List
import csv
import pymysql.cursors
import logging

logging.basicConfig(level=logging.INFO)

class URLRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.urls = self.load_urls()

    def load_urls(self) -> List[str]:
        with open(self.file_path, 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            read_urls = [url for row in csv_reader for url in row]
        return read_urls

    def exists(self, url) -> bool:
        return url in self.urls

    def add_url(self, url: str):
        with open(self.file_path, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([url])
        self.urls.append(url)


class MySQLRepository:
    def __init__(self):
        self.host = 'exit-database.c9heedqt7ayj.ap-northeast-2.rds.amazonaws.com'
        self.user = 'admin'
        self.password = 'fkdls3323'
        self.database = 'foryoutime'
        self.connection = self.connect_to_mysql()

    def connect_to_mysql(self):
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection

    def get_elasped_time(self, url) -> float :
        with self.connection.cursor() as cursor:
            sql = f"SELECT D as elasped_time FROM grade WHERE host = '{url}'"
            print(sql)
            logging.info(sql)
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result['elasped_time'])
            logging.info(result['elasped_time'])
        return int(result['elasped_time'] * 100)
