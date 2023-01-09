# CalendarSetting

## 参考URLまとめ

* google認証系の設定  
`https://www.yutaka-note.com/entry/2020/01/31/141843`

* gmailの連携と基本操作  
`https://montaiblog.com/gmail-apipython/`

* googleCalendarの操作系  
`https://non-dimension.com/python-googlecalendarapi/`

* リフレッシュトークンがうまく動かない場合の対処法[未解決]  
一度token.pickleを消去して、再度アクセス認証をすることで再度動くことは確認済み  
`https://www.cdatablog.jp/entry/gcprefreshtokengrant`

### サービスアカウントによるログインについて  

google apiのサービスアカウントでログインするにはgoogle workspace(有料)のアカウント作成が必要

* 参考URL  
`https://teratail.com/questions/193186`
`https://www.marketechlabo.com/python-google-auth/#%E5%80%8B%E5%88%A5%E3%81%AE%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%82%92%E5%88%A9%E7%94%A8%E3%81%99%E3%82%8B%EF%BC%88%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E3%82%A2%E3%82%AB%E3%82%A6%E3%83%B3%E3%83%88%E3%81%A8%E3%83%A6%E3%83%BC%E3%82%B6%E3%82%A2%E3%82%AB%E3%82%A6%E3%83%B3%E3%83%88%E3%81%A7%E5%85%B1%E9%80%9A%EF%BC%89`
`https://messefor.hatenablog.com/entry/2020/10/08/080414`
`https://zenn.dev/antyuntyun/articles/python_google_drive`

後で読む
`https://isgs-lab.com/727/`

## エラー記録

2023/01/09 gmail_initでエラー
→credentialフォルダの中身をcred_gmail.json,google_service_key.jsonのみすることで動作を確認
→もしかすると定期的にtoken.jsonの削除が必要かも？

2022/03/26 googleAPIでログインできない事象発生中
→メールから取得する情報が空の時に想定しない形で終了していた。修正済み

2022/11/06 一日に複数の予定が入っている場合の処理に想定漏れあり
→判定方法を修正
