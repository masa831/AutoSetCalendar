import re
import os.path
from re import sub
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# gmail参考URL
# https://100webdesign.jp/services/web_knowhow/gmail-api/web_knowhow-22937/

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# token.jsonを定義（実体ファイルは最初はなくてもOK。なければ作る処理を書くので）
tokenPath = "credential/token.json"

# 認証情報ファイルを定義
credentialsPath = "credential/cred_gmail.json"
# ここにはダウンロードした認証情報ファイル名を記述します。
# 同じディレクトリにあるファイルならファイル名だけでOK

def gmail_init():
    """gmailへのアクセス

    gmailへのアクセスを実施

    Args:None

    Returns:
        serviceインスタンス(gmail)

    Note:
        token.pickleを使用するパターンでは期限が切れるため、こちらの形式に変更

    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(tokenPath):
        creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentialsPath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenPath, 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

# メールの一覧を取得
def get_message_list(service, date_from, date_to, message_from, message_to):
    """gmailから対象のメールを検索

    Args:
        service (service(gmail)): gmailのインスタンス
        data_from (str:'xxxx-xx-xx'): メール取得の開始日
        data_to (str:'xxxx-xx-xx'): メール取得の終了日
        message_from (str): 検索対象のメールアドレス
        message_to (str): 自身のメールアドレス

    Returns:
        str[]: 検索結果のメールの中身を取得

    Examples:
        message_list = get_message_list(service, '2022-11-20', '2022-12-31', 'xx@abc.com', 'xxx@gmail.com')

    """
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

def getReleaseDateAndTitle(msrReleaseDate, msrTitle):
    """タイトルと日付を加工する関数

    get_message_listから取得したタイトルと日付を使いやすいように加工する

    Args:
        msrReleaseDate (str): 日付を含んだ文字列(gmail[snippet])
        msrTitle (str): タイトルを含んだ文字列(gmail[Subject])

    Returns:
        dict: {'ReleaseDate':'xxxx-xx-xx','Title':'xxxx'}

    """
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

def getlist(message_list):
    """get_message_listからタイトルと日付を取得する関数

    Args:
        str[]: 検索結果のメールの中身を取得

    Returns:
        dict_list: [{'ReleaseDate':'xxxx-xx-xx','Title':'xxxx'}, xx]

    """
    ret_list = []
    for message in message_list:
        if ('Subject' in message) and ('snippet' in message):
            dictMessage = getReleaseDateAndTitle(message['snippet'],message['Subject'])
            # dictMessageの空欄ペアを除去
            if (dictMessage['ReleaseDate'] != '') and (dictMessage['Title'] != ''):
                ret_list.append(dictMessage)
    return ret_list


# 単体テスト用Main関数
def main():
    service = gmail_init()
    target_address = 'alert@shop-bell.com'
    address = 'xxxx@gmail.com'
    message_list = get_message_list(service, '2022-11-20', '2022-12-31', target_address, address)
    dict_list = getlist(message_list)
    print(dict_list)

# プログラム実行！
if __name__ == '__main__':
    main()


