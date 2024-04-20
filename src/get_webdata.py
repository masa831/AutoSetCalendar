from time import sleep
import re
import datetime
from typing import Dict,List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

import src.userdata as userdata
from src.cstm_logging import CstmLogger

class LoadData():
    def __init__(self):
        self._driver_path = r'drvier\chromedriver.exe'
        self._username = userdata.USERNAME
        self._password = userdata.PASSWORD
        self._output_path = r'data\data.csv'
        self.log = CstmLogger()
        self.log.set_handler()

    def run(self):
        self.log.debug('start login')
        table = self.login()
        self.log.debug('start cransed_data')
        data = self.cransed_data(table)
        self.log.debug('start make_csv')
        self.make_csv(data)
        self.log.debug('start convert_data')
        data_list = self.convert_data(data)
        self.log.debug('process data finish')
        self.log.release_handler()
        return data_list

    def login(self):
        service = webdriver.ChromeService(executable_path=self._driver_path)
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)
        target_url = 'https://alert.shop-bell.com/'
        # 初期アクセス
        driver.get(target_url)
        sleep(1)

        # loginページ遷移
        login_page = 'https://alert.shop-bell.com/users/login/'
        driver.get(login_page)
        sleep(1)

        # username設定
        username_input = driver.find_element(By.XPATH, "//input[@id='Email']")
        username_input.send_keys(self._username)
        sleep(1)

        # password設定
        password_input = driver.find_element(By.XPATH, "//input[@id='Password']")
        password_input.send_keys(self._password)
        sleep(1)

        # loginボタン押下
        login_button = driver.find_element(By.XPATH, "//button[@type='submit' and @class='btn']")
        login_button.click()
        sleep(1)

        # 一覧ページへ遷移
        list_page = 'https://alert.shop-bell.com/users/alert_list/'
        driver.get(list_page)
        sleep(1)

        # table全体を取得
        table = driver.find_element(By.XPATH, "//tbody")

        # table内の情報をlistへ変換
        table_data = []
        for tr_element in table.find_elements(By.XPATH, ".//tr"):
            data_row = [td.text for td in tr_element.find_elements(By.XPATH, ".//td")]
            table_data.append(data_row)

        # driverの終了
        driver.quit()

        return table_data


    def cransed_data(self,table_data):

        # dataframeへ変換
        df = pd.DataFrame(table_data)
        # 欠損値があるものは排除
        df = df.dropna(how='any')

        # 戻り値のデータ型を生成
        df_result = pd.DataFrame(columns=['title','num_turns','num_turns_next','release','release_next','status'])

        # 値をセット
        df_result['title'] = df[1].apply(self.cransed_title)
        df_result['release'] = df[3].apply(self.change_datatime)
        df_result['num_turns'] = df[4]
        df_result['release_next'] = df[5].apply(self.change_datatime)
        df_result['num_turns_next'] = df[6]

        return df_result


    def cransed_title(self, title: str) -> str:
        ret = ''
        match = re.search(r'タイトル：\n(.*?)\n著者：', title)
        if match:
            ret = match.group(1)
        else:
            ret = 'Error: cransed_title'
        return ret


    def change_datatime(self, date_str):
        date_pattern = r"(\d{4})年(\d{1,2})月(\d{1,2})日"  # Capture year, month, and day
        expected_pattern = r"\((\d{4})年(\d{1,2})月(\d{1,2})日頃\)"  # Capture expected release date

        # Match against the date pattern
        date_match = re.search(date_pattern, date_str)
        expected_match = re.search(expected_pattern, date_str)

        if date_match:
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            day = int(date_match.group(3))

            release_date = f"{year}-{month:02}-{day:02}"

        elif expected_match:
            expected_year = int(expected_match.group(1))
            expected_month = int(expected_match.group(2))
            expected_day = int(expected_match.group(3))

            release_date = f"{expected_year}-{expected_month:02}-{expected_day:02}"

        else:
            release_date = ''

        return release_date


    def make_csv(self, data):
        data.to_csv(self._output_path, encoding='cp932')

    def convert_data(self, data):
        
        # [{'ReleaseDate':'xxxx-xx-xx','Title':'xxxx'},xx]
        ret_list = []
        # Get the current date
        current_date = pd.to_datetime('today')
        df_tmp = data.copy()
        df_tmp = df_tmp[df_tmp['release_next'] != '']

        df_tmp['release_next'] = pd.to_datetime(df_tmp['release_next'])

        # Calculate the start and end dates of the one-month range
        one_month_range = pd.DateOffset(months=1)
        start_date = current_date - one_month_range
        end_date = current_date + one_month_range

        # # Filter rows within the one-month range
        df_filter = df_tmp[df_tmp['release_next'].between(start_date, end_date)]
        
        for ind,row in df_filter.iterrows():
            dict_row = {'ReleaseDate':'','Title':''}
            title = row['title']+':'+row['num_turns_next']
            date = row['release_next'].strftime('%Y-%m-%d')

            dict_row['ReleaseDate'] = date
            dict_row['Title'] = title

            ret_list.append(dict_row)
        
        return ret_list

