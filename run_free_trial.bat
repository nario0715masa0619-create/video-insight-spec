@echo off
REM 無料1本解析 実行バッチ（Windows）
REM 使い方: run_free_trial.bat trial_companyx_20260609

setlocal enabledelayedexpansion

if "%1"=="" (
    echo ❌ 使い方: run_free_trial.bat {case_id}
    echo.
    echo 例: run_free_trial.bat trial_companyx_20260609
    exit /b 1
)

set CASE_ID=%1

echo 🚀 無料1本解析を開始します...
echo 案件ID: %CASE_ID%
echo.

python scripts/run_free_trial_one_video.py --case-id %CASE_ID%

if errorlevel 1 (
    echo.
    echo ❌ エラーが発生しました
    echo ログを確認してください: free_trial_cases\logs\%CASE_ID%.log
    exit /b 1
)

echo.
echo ✅ 完了しました！
echo 成果物は以下に出力されています:
echo free_trial_cases\deliverables\%CASE_ID%\
pause
