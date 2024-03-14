import pymysql.cursors
import logging

logging.basicConfig(level=logging.INFO)


class MySQLRepository:
    def __init__(self):
        self.host = 'exit-database.c9heedqt7ayj.ap-northeast-2.rds.amazonaws.com'
        self.user = 'admin'
        self.password = 'fkdls3323'
        self.database = 'foryoutime'
        self.connection = self.connect_to_mysql()
        self.url_cache = self.load_url_cache()

    def connect_to_mysql(self):
        connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection

    def get_connection(self):
        try:
            self.connection.ping(reconnect=True) # Check if the connection is alive, reconnect if not
        except (AttributeError, pymysql.OperationalError):
            # If the connection is not established or has been closed, reconnect
            self.connection = self.connect_to_mysql()


    def get_elasped_time(self, url) -> float:
        self.get_connection()
        with self.connection.cursor() as cursor:
            sql = f"SELECT D as elasped_time FROM grade WHERE host = '{url}'"
            print(sql)
            logging.info(sql)
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None :
                return 150
            print(result['elasped_time'])
            logging.info(result['elasped_time'])
        return int(result['elasped_time'] * 1000)

    def load_url_cache(self):
        url_cache = set()
        try:
            self.get_connection()
            with self.connection.cursor() as cursor:
                sql = "SELECT url FROM urls"
                cursor.execute(sql)
                result = cursor.fetchall()
                for row in result:
                    url_cache.add(row['url'])
        except Exception as e:
            logging.error(f"Error loading URL cache: {str(e)}")
            raise
        return url_cache

    def exists_url(self, url: str) -> bool:
        return url in self.url_cache

    def add_url(self, url: str) -> None:
        try:
            self.get_connection()
            with self.connection.cursor() as cursor:
                sql = f"INSERT INTO urls (url) VALUES ('{url}')"
                logging.info(sql)
                cursor.execute(sql)
            self.connection.commit()
            self.url_cache.add(url)  # 새로운 URL을 캐시에 추가
        except Exception as e:
            logging.error(f"Error adding URL to database: {str(e)}")
            raise

    def get_all_urls(self) -> list:
        try:
            self.get_connection()
            with self.connection.cursor() as cursor:
                sql = "SELECT url FROM urls"
                cursor.execute(sql)
                result = cursor.fetchall()
                return [row['url'] for row in result]
        except Exception as e:
            logging.error(f"Error fetching all URLs from database: {str(e)}")
            raise

    def close(self):
        self.connection.close()