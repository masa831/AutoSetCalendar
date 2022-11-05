% echo off
rem このファイルの配置フォルダをカレントにする
pushd %0\..
rem 画面をクリア
cls
rem pythonスクリプトを実行
python C:\Users\zeroc\work\autoSetCalendar\main.py
rem 30秒間待機
timeout /t 30