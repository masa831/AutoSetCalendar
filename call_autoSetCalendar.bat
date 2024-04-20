% echo off
rem このファイルの配置フォルダをカレントにする
pushd %0\..
rem 画面をクリア
cls
rem 仮想環境起動
cd C:\Users\zeroc\work\autoSetCalendar
call env_c\Scripts\activate
rem pythonスクリプトを実行
python C:\Users\zeroc\work\autoSetCalendar\main.py
rem 30秒間待機
rem timeout /t 30
rem ポーズ
pause
rem 仮想環境の終了
call deactivate