import datetime
import googleapiclient.discovery
import google.auth

# googleCalendar ServiceAccount Login Version
# 参考URL
# https://kosuke-space.com/google-calendar-api-python

# Google APIの準備をする
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Googleの認証情報をファイルから読み込む
gapi_creds = google.auth.load_credentials_from_file('credential/google_service_key.json', SCOPES)[0]
# APIと対話するためのResourceオブジェクトを構築する
service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)

# 認証情報ファイルを定義
credentialsPath = 'credential/google_service_key.json'

def gCalendar_init():
    # Googleの認証情報をファイルから読み込む
    gapi_creds = google.auth.load_credentials_from_file(credentialsPath, SCOPES)[0]
    # APIと対話するためのResourceオブジェクトを構築する
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)
    return service

# 書き込む予定情報を用意する
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

def writeCalendar(serviceCalendar,dict_list,CALENDAR_ID):
    if len(dict_list) == 0:
        print('No New Item')
        return

    for list in dict_list:
        # カレンダー探索用のISO形式の日付を取得
        # list['Release']をdatetime型、ISO形式へ順次変換
        daytmp = datetime.datetime.strptime(list['ReleaseDate'],'%Y-%m-%d')
        StartDay = daytmp.isoformat() + 'Z'
        EndDay = datetime.datetime(daytmp.year,daytmp.month,daytmp.day,23,59).isoformat() + 'Z'

        # 取得したカレンダーにすでに同一の予定があるかを確認
        events_result = serviceCalendar.events().list(calendarId=CALENDAR_ID, timeMin=StartDay, timeMax=EndDay,
                    maxResults=10, singleEvents=True,orderBy='startTime').execute()
        # 取得した情報から内容の抜き出してeventsに格納
        events = events_result.get('items', [])
        str_case = ""

        for numSetCalName in range(len(events_result.get('items', []))):
            # 既に予定があるかを判定
            str_case = "add_event"
            if(events[numSetCalName]['summary'] == list['Title']):
                str_case = "already"
                break

        if str_case == "add_event":
            # 書き込む予定の情報を設定
            body = setBody(list['Title'],list['ReleaseDate'])
            # 設定したbodyの情報で予定を作成
            event = serviceCalendar.events().insert(calendarId=CALENDAR_ID, body=body).execute()
            print('Add Item : [' + list['ReleaseDate'] +']['+ list['Title']+']')
        elif str_case == "already":
            print('This Item already exit : [' + list['ReleaseDate']+']['+list['Title']+']')
        else:
            pass

# 単体テスト用Main関数
def main():
    address = 'xx@gmail.com' # 使用者のアドレスを使用
    service = gCalendar_init()

    list = [{'ReleaseDate': '2023-01-08', 'Title': 'Test1'}, 
    {'ReleaseDate': '2023-01-10', 'Title': 'test2'},
    {'ReleaseDate': '2023-01-08', 'Title': 'Test1'}]
    # writeCalendar(service,list,address)

    no_list = []
    # writeCalendar(service,no_list,address)


# プログラム実行！
if __name__ == '__main__':
    main()
