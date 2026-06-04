@echo off
echo ========================================================
echo Video Insight Spec - Dashboard Demo
echo ========================================================
echo.
echo ダッシュボードを起動しています...
echo ブラウザが自動的に開くまでしばらくお待ちください。
echo (終了する場合はこのウィンドウを閉じるか、Ctrl+Cを押してください)
echo.

streamlit run streamlit_app/app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 起動に失敗しました。以下の点を確認してください。
    echo 1. Pythonがインストールされているか
    echo 2. 初期セットアップ(pip install -r streamlit_app/requirements.txt)が完了しているか
    echo.
    pause
)
