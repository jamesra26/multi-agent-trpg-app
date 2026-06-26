:: Open web server
@echo off
setlocal

set "ROOT=%~dp0.."
set "PYTHON=%ROOT%\.venv\Scripts\python.exe"
set "BACKEND=%ROOT%\backend"

if not exist "%PYTHON%" (
    echo [����] δ�ҵ����⻷��: %ROOT%\.venv
    echo ��������Ŀ��Ŀ¼ִ��: python -m venv .venv
    echo Ȼ��: .venv\Scripts\pip install -e "backend/.[dev]"
    pause
    exit /b 1
)

cd /d "%BACKEND%"
echo [����] http://127.0.0.1:8000
echo [�ĵ�] http://127.0.0.1:8000/docs
echo �� Ctrl+C ֹͣ����
echo.

"%PYTHON%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
