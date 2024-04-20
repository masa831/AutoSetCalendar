from src.get_webdata import LoadData
from src.g_calendar import MyCalendar
import src.userdata as userdata

def main():
    # webpageからデータを取得
    data = LoadData()
    data_list = data.run()
    # カレンダーにセット
    address = userdata.USERNAME
    calendar = MyCalendar(address,data_list)
    calendar.run()

# プログラム実行！
if __name__ == '__main__':
    main()
