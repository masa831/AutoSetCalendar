# gmailから予定を取得し、googleカレンダーに反映
# -*- coding: utf-8 -*-

import datetime
import re
import pickle
import os.path
import base64
from re import sub
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from infoPersonal import InfomationPersonal
from infoPersonal import InfomationSearch
from google.oauth2 import credentials,service_account

# Gmail APIのスコープを設定。
# SCOPESを変更したときはtoken.pickleを消去して再度認証を行う必要がある点に注意
SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/gmail.readonly']

# APIに接続
def connect_googleapi():
    # Google にcalendar/gmailへのアクセストークンを要求してcredsに格納します。
    # 戻り値用の辞書を定義
    dict = {'serviceGmail':'','serviceCalendar':''}
    # credsを初期化
    creds = None
    # アクセストークンを格納しているファイルからトークンを取り出す
    # 有効なトークンをすでに持っているかチェック（２回目以降の実行時に認証を省略するため） 
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # トークンがない場合、アクセストークンの有効期限が切れてる
    # 期限切れのトークンを持っているかチェック（認証を省略するため）
    if not creds or not creds.valid:
        # 有効期限が切れている場合、トークンをリフレッシュ
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # アクセストークンを要求　トークンがない場合、認証画面を表示し、認証完了後トークンを取得
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # アクセストークン保存（２回目以降の実行時に認証を省略するため）
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Gmail API操作に必要なインスタンス作成
    dict['serviceGmail'] = build('gmail', 'v1', credentials=creds)
    # カレンダーAPI操作に必要なインスタンス作成
    dict['serviceCalendar'] = build('calendar', 'v3', credentials=creds)
    
    # return sevice
    return dict

# google apiのサービスアカウントでログインするにはgoogle workspace(有料)のアカウント作成が必要
def connect_api_service():
     # 戻り値用の辞書を定義
    dict = {'serviceGmail':'','serviceCalendar':''}
    # credsを初期化
    creds = None
    # サービスアカウントでの認証
    credentials = service_account.Credentials.from_service_account_file('service_credentials.json')
    creds = credentials.with_scopes(SCOPES)

    # Gmail API操作に必要なインスタンス作成
    dict['serviceGmail'] = build('gmail', 'v1', credentials=creds)
    # カレンダーAPI操作に必要なインスタンス作成
    dict['serviceCalendar'] = build('calendar', 'v3', credentials=creds)

    # return sevice
    return dict


# メールの一覧を取得
def get_message_list(service, date_from, date_to, message_from, message_to):
    message_list = []
    query = ''
    # 検索用クエリを指定する
    if date_from != None and date_from != '':
        query += 'After:' + date_from + ' '
    if date_to != None and date_to != '':
        query += 'Before:' + date_to + ' '
    if message_from != None and message_from != '':
        query += 'From:' + message_from + ' '
    if message_to != None and message_to != '':
        query += 'To:' + message_to + ' '

    # メールIDの一覧を取得する(最大100件)
    messageid_list = service.users().messages().list(userId='me', maxResults=100, q=query).execute()

    # 該当するメールが存在しない場合は、処理中断
    if messageid_list['resultSizeEstimate'] == 0:
        print('Message is not found')
        return message_list
    # メッセージIDを元に、メールの詳細情報を取得
    for message in messageid_list['messages']:
        row = {}
        row['ID'] = message['id']
        message_detail = service.users().messages().get(userId='me', id=message['id']).execute()
        for header in message_detail['payload']['headers']:
            # 日付、送信元、件名を取得する
            if header['name'] == 'Date':
                row['Date'] = header['value']
            elif header['name'] == 'From':
                row['From'] = header['value']
            elif header['name'] == 'To':
                row['To'] = header['value']
            elif header['name'] == 'Subject':
                row['Subject'] = header['value']
        # snippet をrowに格納
        row['snippet'] = message_detail['snippet']
        # message_listにrowを格納
        message_list.append(row)

    return message_list

# get_message_listからタイトルと日付を取得する関数
def getReleaseDateAndTitle(msrReleaseDate, msrTitle):
    # 戻り値用の辞書を定義
    dict = {'ReleaseDate':'','Title':''}
    # 値格納用ローカル変数
    TitleName = '' 
    ReleaseDate = ''

    # メールのタイトルが予約受付開始であれば、メールの構造の中から発売日の日付を取得
    checkTitle = re.search('【予約受付開始】',msrTitle)

    # checkTitleの値があるかを確認
    if (str(checkTitle) != 'None') :
        # タイトルに予約受付開始があれば、ReleaseDate,TitleNameを取得
        if ( checkTitle.group() == '【予約受付開始】'):
                # 日付箇所のみを取得
                match = re.search('20[0-9]+年[0-9]+月[0-9]+日',msrReleaseDate)
                temp = match.group()
                # x年x月x日からx-x-xの形式に変換
                temp1 = temp.rstrip('日')
                temp2 =  temp1.translate(str.maketrans({'年':'-','月':'-'}))
                ReleaseDate = temp2 
                #print(ReleaseDate)
                # タイトルのみを取得　分割後 ['','タイトル','']の形で出力
                split = re.split('【予約受付開始】|【ベルアラート】',msrTitle)
                TitleName = split[1]
                #print(TitleName)

    # dictに格納
    dict['ReleaseDate'] = ReleaseDate
    dict['Title'] = TitleName

    return dict

# 日付取得関数_str
def getDate():
    # 戻り値用の辞書を定義
    dict = {'EndDay':'','StartDay':''}
    # プログラム起動時の日付とその30日前の日付を取得
    dt_now = datetime.datetime.now()
    dt_diff = datetime.timedelta(days=30)
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

def setBody(title,day):

    # dayをdatetime型へ変換
    tmpday = datetime.datetime.strptime(day,'%Y-%m-%d')
    # dayに1日を加算する
    deltaday_t = tmpday + datetime.timedelta(days=1)
    # dayの翌日を文字列に変換
    deltaday = deltaday_t.strftime('%Y-%m-%d')

    # 終日の予定を入れるときはdateにstrを格納。
    # 時間指定の予定を入れるときはdateTimeにdatetimeのISO形式を格納
    body = {
        # 予定のタイトル
        'summary': title,
        'allDayEvent': True,
        # 予定の開始時刻
        'start': {
            #'dateTime': datetime.datetime(2021, 12, 17, 10, 30).isoformat(),
            'date': day,
            'timeZone': 'Japan'
        },
        # 予定の終了時刻
        'end': {
            # 'dateTime': datetime.datetime(2021, 12, 17, 12, 00).isoformat(),
            'date': deltaday,
            'timeZone': 'Japan'
        },
        'reminders': {'useDefault': False}
    }
    return body

# メイン処理
def main():
    # 情報設定用のインスタンスを設定
    infoPersonal = InfomationPersonal()
    infoSearch = InfomationSearch()

    # メール検索用の日付の文字列を取得
    dict_day = getDate()
    dict_day_iso = getDataISO()

    # 発売日とタイトルの辞書を格納するためにリストを用意
    dict_list = []

    # gmail/calendar操作用のインスタンス作成
    service = connect_googleapi()
    serviceGmail = service['serviceGmail']
    serviceCalendar = service['serviceCalendar']

    # サービスアカウントテスト
    # service = connect_api_service()
    # serviceGmail = service['serviceGmail']
    # serviceCalendar = service['serviceCalendar']

    # 検索条件に一致したメールのタイトルを取得
    #message_list = get_message_list(service, dict_day['StartDay'], dict_day['EndDay'], infoSearch.SEARCH_MAIL_ADDRESS, infoPersonal.MY_MAIL_ADDRESS)
    message_list = get_message_list(serviceGmail, dict_day['StartDay'], dict_day['EndDay'], infoSearch.SEARCH_MAIL_ADDRESS, infoPersonal.MY_MAIL_ADDRESS)
    
    # 検索したメールから必要な情報をdict_listに格納
    for message in message_list:
        if ('Subject' in message) and ('snippet' in message):
            dictMessage = getReleaseDateAndTitle(message['snippet'],message['Subject'])
            # dictMessageの空欄ペアを除去
            if (dictMessage['ReleaseDate'] != '') and (dictMessage['Title'] != ''):
                dict_list.append(dictMessage)

    # カレンダーから予定を取得 timeMin,timeMaxはISO形式で指定
    # events_result = serviceCalendar.events().list(calendarId='primary', 
    #                     timeMin=dict_day_iso['StartDay'],timeMax=dict_day_iso['EndDay'],
    #                     maxResults=100, singleEvents=True,orderBy='startTime').execute()
    # 予定があった場合には、出力
    # for event in events:
    #     # 予定の日付をstartに格納
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     print(start, event['summary'])
        
    # Gmailから取得したリストに対して、カレンダーへの追加を実施
    for list in dict_list:
        try:
            print('処理を開始します')
            # カレンダー探索用のISO形式の日付を取得
            # list['Release']をdatetime型、ISO形式へ順次変換
            dayISO = datetime.datetime.strptime(list['ReleaseDate'],'%Y-%m-%d').isoformat() + 'Z' 

            # 取得したカレンダーにすでに同一の予定があるかを確認
            events_result = serviceCalendar.events().list(calendarId='primary', timeMin=dayISO,
                        maxResults=1, singleEvents=True,orderBy='startTime').execute()
            # 取得した情報から内容の抜き出してeventsに格納
            events = events_result.get('items', [])

            # 既に予定があるかを判定
            if(events[0]['summary'] != list['Title']):
                # 書き込む予定の情報を設定
                body = setBody(list['Title'],list['ReleaseDate'])
                # 設定したbodyの情報で予定を作成
                event = serviceCalendar.events().insert(calendarId='primary', body=body).execute()
                print( list['ReleaseDate']+'に'+list['Title']+'の発売予定を追加しました')
            elif(events[0]['summary'] == list['Title']):
                print(list['ReleaseDate']+'の'+list['Title']+'の予定はすでに追加されています。')

        except:
            print('エラーが発生しました')
        else:
            print('処理は正常に終了しました')


# プログラム実行！
if __name__ == '__main__':
    main()


