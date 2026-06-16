@echo off
setlocal

set "ROOT=%~dp0.."
set "PYTHON=%ROOT%\.venv\Scripts\python.exe"
set "BACKEND=%ROOT%\backend"

if not exist "%PYTHON%" (
    echo [错误] 未找到虚拟环境: %ROOT%\.venv
    echo 请先在项目根目录执行: python -m venv .venv
    echo 然后: .venv\Scripts\pip install -e "backend/.[dev]"
    pause
    exit /b 1
)

cd /d "%BACKEND%"
echo [启动] http://127.0.0.1:8000
echo [文档] http://127.0.0.1:8000/docs
echo 按 Ctrl+C 停止服务
echo.

"%PYTHON%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
