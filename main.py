# gmailから予定を取得し、googleカレンダーに反映
# -*- coding: utf-8 -*-

import datetime
from re import sub
from googleapiclient.discovery import build
from infoPersonal import InfomationPersonal,InfomationSearch
import service_gmail,service_googlecalendar

# 日付取得関数_str
def getDate():
    # 戻り値用の辞書を定義
    dict = {'EndDay':'','StartDay':''}
    # プログラム起動時の日付とその30日前の日付を取得
    dt_now = datetime.datetime.now()
    dt_diff = datetime.timedelta(days=50)
    dt_before = dt_now - dt_diff

    dict['EndDay'] =dt_now.strftime('%Y-%m-%d')
    dict['StartDay'] = dt_before.strftime('%Y-%m-%d')
    return dict

# 日付取得関数_ISOformat
def getDataISO():
    # 戻り値用の辞書を定義
    dict = {'EndDay':'','StartDay':''}
    # プログラム起動時の日付とその30日前の日付を取得
    dt_now = datetime.datetime.now()
    dt_diff = datetime.timedelta(days=30)
    dt_before = dt_now - dt_diff

    # 'Z' indicates UTC time
    dict['EndDay'] =dt_now.isoformat() + 'Z'  
    dict['StartDay'] = dt_before.isoformat() + 'Z'
    return dict

# メイン処理
def main():
    print('[Start]')
    try:
        # インスタンス作成
        infoPersonal = InfomationPersonal()
        infoSearch = InfomationSearch()
        service_mail = service_gmail.gmail_init()
        service_calendar = service_googlecalendar.gCalendar_init()

        # メール検索用の日付の文字列を取得
        dict_day = getDate()
        # gmailから過去30日の情報を取得
        message_list = service_gmail.get_message_list(
            service_mail,
            dict_day['StartDay'],
            dict_day['EndDay'],
            infoSearch.SEARCH_MAIL_ADDRESS,
            infoPersonal.MY_MAIL_ADDRESS)
        dict_list = service_gmail.getlist(message_list)
        # カレンダーに反映
        service_googlecalendar.writeCalendar(service_calendar,dict_list,infoPersonal.MY_MAIL_ADDRESS)
        print('[process is succesful]')
    except:
        print('[An error has occurred]')

# プログラム実行！
if __name__ == '__main__':
    main()
