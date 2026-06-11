@echo off
REM ===============================================
REM Free-Trial Dashboard Launcher v1.5.7
REM Life Design Partners
REM ===============================================

echo.
echo [*] Free-Trial Dashboard v1.5.7 起動中（Life Design Partners）...
echo.

REM プロセス停止
echo [Step 1] 既存プロセスを停止...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM streamlit.exe >nul 2>&1
timeout /t 2 /nobreak

REM キャッシュ削除
echo [Step 2] Streamlit キャッシュを削除...
rmdir /S /Q "%USERPROFILE%\.streamlit" >nul 2>&1
timeout /t 1 /nobreak

REM 環境変数設定
echo [Step 3] 環境変数を設定...
set VIS_MODE=free_trial
set PYTHONIOENCODING=utf-8

REM Streamlit 起動
echo [Step 4] Streamlit を起動します...
echo.
echo ===============================================
echo Local URL: http://localhost:8501
echo Network URL: http://192.168.0.241:8501
echo ===============================================
echo.

streamlit run streamlit_app/app.py --server.port=8501

pause
