%echo off
rem このファイルの配置フォルダをカレントにする
pushd %0\..
rem 画面をクリア
cls
rem pythonスクリプトを実行
python C:\Users\zeroc\work\autoSetCalendar\main.py
rem 実行するpythonスクリプトファイル"hello.py"はフルパスで指定します。
rem 実行はウインドウは開いたままにする
pause