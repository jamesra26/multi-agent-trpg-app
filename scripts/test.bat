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
echo [测试] 运行 pytest...
echo.

"%PYTHON%" -m pytest -v
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% neq 0 goto :failed

echo.
echo [完成] 全部测试通过
goto :done

:failed
echo.
echo [失败] 存在未通过的测试

:done
echo.
pause
exit /b %EXIT_CODE%
