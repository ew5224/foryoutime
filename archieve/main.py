import pandas as pd
import urllib3
import time
import statistics
import socket
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
import sys, os

# 한글 폰트 등록


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):  # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath("..")

    return os.path.join(base_path, relative_path)

LabelBase.register(name='NanumGothic', fn_regular=resource_path('NanumGothic-Regular.ttf'))

def get_google_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    ouath_json = {
        "type": "service_account",
        "project_id": "line-sideproject",
        "private_key_id": "789b6774a11ed2211add36339fe6eca851a35606",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQChqNkJmarNijVO\n/iN5b6iWJ4Btiq5eVRcmiY1wKGL/0OnxR6ZZ17mS9ALapr/55wgSaIXmuJ2aPCL8\nj8vgf/q5hdVBfitsg5RkgG6LA0OJSPF/nkxOde77oxGggUdN8szls9Cl2BxkJ84c\n2iKxT0xLNIYEbIQIuYnDitnd7ZuVRKm2RfpTrRnEf4M7o/XBhOSpnrOlfY5IuVk0\nqLFS5sFA0Ek+bjh9bz+qyxpYBEw7Bur5hWckHDbHV2Gg5qvCVBoAbPfvCR83Rb7a\ndkJ4FojQNJj7TdKO67I2xbBztAUVOMi1wyHFJVg+Dp/yKzaCgtqF4BfOJ3TPkPj1\n3kewJ7efAgMBAAECggEAM5tc6fEp8yK3YOfFeFtaZNDocU/P2WJtmQpZYiAqdoMB\nY9qdMtoork6CaL3J1GPaElJWyLBP87BV9O2MxrbkWfxs91LpVuNsaGcNowggM7/b\nBIQK1RNV/vPwSR5sHmiv23Z7Wa4zZg/E/zXt1E+9ydZTIC9qOQTOA2Qcp/nV7KD0\naiGsaa3CtdaoyIGrnj7HjB2NgzCGAuckq0S3DiBbhSkiet9GssjGTAY3OW4g533i\nFVq9ENEbw97IRFbYB+EDbi9dUqGEq2Wqqp0vCKMHpJTc66VvW9zZDd+GmNfsyqtm\n9Efj9LITSjPcW5M+WUNXWELZa5xhuW1OXRTB53vXuQKBgQDPN9YXFykdrJUv7631\nL/d5Vj0wJ4we7hWrpYlQGHZPVgb/9fzG/z4190d3lF89Zjd8VF/du0fwYjxYRq+/\nRFRkheafVXDQbk9Fy6ysktTSm/d16dsaQ9oE24Ne0rcUO9p4BbRHmBeQO4l6xEHT\np4IqRidqTiEY9umUp8IIi1l1OQKBgQDHt2OzJ+6f7dSZNmIIxJKUT+xG4g2jEkKg\nIxQFR/rMT9yUv/BbQ94ynY/xQGzlTmRVdDXGcv0/N/pVZJPHqI/fSY7Wgr1ZZqWU\nFxqRsdCaVB7F1Y25pEZP8Ue71z/Q8rgwTWY42Lcf5KALupJkyemY8Ar7gBakHaEJ\npGrBIEsrlwKBgCgOti8+he87lpdusOUuAZwOJMPzUS4FfmDxHitCn1RU4AOJDPV3\nEBKkm8ctAoA/C0jYkrOtaYm5o8q4126VCe9oxx1UCfvw5xgp+FZgCA4yolLEA1v/\nc9zuhmXFPCkILQJ4r9ILP7rdF4WI/OSqhAoiB6qQMeu+h4b6KxM1xPRZAoGAGPkq\no2Vz5lW0BvCQ86248ojH79kmgWSwJhwczchBaTj3STZzFMZ4y3V+YVmABHB4BWOB\nse4BEt2qFPF9tTKzwuUM0nAIw1wdilYVQXCtuA6axnw8u6D6FdcC9E8nMLaZJ5kW\nFjerNna9OJo84hOJfVFO3kIXErCNyYngu4ORQsMCgYEAtUZ00Y6UEkdcu/Sh3efh\nTlYA3AsbeN+NPcbJ+hq0F+W0RlogmPeknS7LMzFOu6+jlljtkmV+BHxgcLVfsdoD\nNsrBUDi2jFpr8tm+gaq89yB1/aA8LbKNR5xZFJ5Qc/Ywh5hL9H2lQT4t+kwiF+Ss\n7Dta721LvPC/nXU283LkxmA=\n-----END PRIVATE KEY-----\n",
        "client_email": "line-sideproject@line-sideproject.iam.gserviceaccount.com",
        "client_id": "101855715061974207460",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/line-sideproject%40line-sideproject.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

    # json_key_path = "./test.json"  # JSON Key File Path

    credential = ServiceAccountCredentials.from_json_keyfile_dict(ouath_json, scope)
    gc = gspread.authorize(credential)

    # URL로 열기
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/17fAwIk5Q2OIW-E3T81dFCmix0pW-bQieUcJJGzvSFyk/edit#gid=0"
    sheet = gc.open_by_url(spreadsheet_url).sheet1

    return sheet


def append_to_sheet(elasped_time_df: pd.DataFrame, sheet):
    print("Start Append to Google Sheet ... ")
    for _, row in elasped_time_df.iterrows():
        sheet.append_row(row.tolist())

    print("Successfully Append")


def elasped_time_checker(host_list: list[str], http: urllib3.PoolManager, checker_name: str, checker_location: str,
                         test_num: int = 10) -> pd.DataFrame:
    elapsed_times = []
    status_codes = {}

    columns = ['checker', 'location', 'checktime', 'url', 'average', 'median', 'min', 'max', 'stdev', 'ip address']
    elasped_time_df = pd.DataFrame(columns=columns)
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')

    for host in host_list:
        ip_address = socket.gethostbyname(host)
        for i in range(test_num):
            start_time = time.time()
            response = http.request('GET', host)
            end_time = time.time()

            elapsed_time = end_time - start_time
            elapsed_times.append(elapsed_time)

            status_code = response.status
            status_codes[status_code] = status_codes.get(status_code, 0) + 1
            # print(f"Request {i + 1}, Status Code: {status_code}, Elapsed Time: {elapsed_time}")

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
        elasped_time_df.loc[len(elasped_time_df)] = [checker_name, checker_location, current_time, host, average_time, median_time, min_time, max_time, std_dev_time, ip_address]

    return elasped_time_df

class CheckerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        self.checker_input = TextInput(hint_text='Checker Name',font_name='NanumGothic')
        self.location_input = TextInput(hint_text='Checker Location', font_name='NanumGothic')

        execute_btn = Button(text='Execute', font_name='NanumGothic')
        execute_btn.bind(on_press=self.run_code_with_running)

        self.output = TextInput(readonly=True, background_color=(1, 1, 1, 0.8), font_name='NanumGothic')

        layout.add_widget(self.checker_input)
        layout.add_widget(self.location_input)
        layout.add_widget(execute_btn)
        layout.add_widget(self.output)

        return layout

    def run_code_with_running(self, instance) :
        self.output.text = "Running..."
        Clock.schedule_once(self.run_code, 0.1)

    def run_code(self, instance):
        import io
        import sys
        # Output redirection
        old_stdout, old_stderr = sys.stdout, sys.stderr
        new_stdout = io.StringIO()
        sys.stdout, sys.stderr = new_stdout, new_stdout

        try:
            host_list = ["app.catchtable.co.kr", "tickets.interpark.com", "portal.yonsei.ac.kr", "pusan.ac.kr",
                         "jejunu.ac.kr",
                         "ticket.melon.com", "letskorail.com", "facebook.com"]
            http = urllib3.PoolManager()
            checker = self.checker_input.text
            check_location = self.location_input.text
            elasped_time_df = elasped_time_checker(host_list, http, checker_name=checker,
                                                   checker_location=check_location)
            append_to_sheet(elasped_time_df, sheet=get_google_sheet())
            output_text = "Execution Successful."
        except Exception as e:
            output_text = f"Error: {e}"

        sys.stdout, sys.stderr = old_stdout, old_stderr
        final_output = new_stdout.getvalue()
        final_output = final_output + "\n\n" + "Google Sheet link : https://docs.google.com/spreadsheets/d/17fAwIk5Q2OIW-E3T81dFCmix0pW-bQieUcJJGzvSFyk/edit#gid=0"

        self.output.text = output_text + "\n\n" + final_output


if __name__ == '__main__':
    CheckerApp().run()


