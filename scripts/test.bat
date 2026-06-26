@echo off
setlocal

set "ROOT=%~dp0.."
set "PYTHON=%ROOT%\.venv\Scripts\python.exe"
set "BACKEND=%ROOT%\backend"
set "TARGET=%~1"

if "%TARGET%"=="" set "TARGET=all"

if not exist "%PYTHON%" (
    echo [error] Virtual environment not found: %ROOT%\.venv
    echo Create it from repo root:
    echo   python -m venv .venv
    echo Then install dev dependencies:
    echo   .venv\Scripts\pip install -e "backend/.[dev]"
    pause
    exit /b 1
)

cd /d "%BACKEND%"

call :install_dev_dependencies
set "EXIT_CODE=%ERRORLEVEL%"
if errorlevel 1 goto :failed

if /i "%TARGET%"=="lint" (
    call :lint
    goto :after_target
)
if /i "%TARGET%"=="pytest" (
    call :pytest
    goto :after_target
)
if /i "%TARGET%"=="coverage" (
    call :coverage
    goto :after_target
)
if /i "%TARGET%"=="all" goto :all

echo [error] Unknown workflow: %TARGET%
echo Usage:
echo   scripts\test.bat lint
echo   scripts\test.bat pytest
echo   scripts\test.bat coverage
echo   scripts\test.bat all
pause
exit /b 1

:install_dev_dependencies
echo [setup] Installing backend dev dependencies...
echo.
"%PYTHON%" -m pip install -e ".[dev]"
exit /b %ERRORLEVEL%

:all
call :lint
set "EXIT_CODE=%ERRORLEVEL%"
if errorlevel 1 goto :failed
call :pytest
set "EXIT_CODE=%ERRORLEVEL%"
if errorlevel 1 goto :failed
call :coverage
set "EXIT_CODE=%ERRORLEVEL%"
if errorlevel 1 goto :failed
goto :passed

:after_target
set "EXIT_CODE=%ERRORLEVEL%"
if %EXIT_CODE% neq 0 goto :failed
goto :passed

:lint
echo [workflow] lint: ruff check .
echo.
"%PYTHON%" -m ruff check .
exit /b %ERRORLEVEL%

:pytest
echo [workflow] pytest: pytest -v
echo.
"%PYTHON%" -m pytest -v
exit /b %ERRORLEVEL%

:coverage
echo [workflow] coverage: pytest --cov=app --cov-report=term-missing --cov-report=xml
echo.
"%PYTHON%" -m pytest --cov=app --cov-report=term-missing --cov-report=xml
exit /b %ERRORLEVEL%

:passed
set "EXIT_CODE=0"
echo.
echo [ok] Workflow passed: %TARGET%
goto :done

:failed
echo.
echo [failed] Workflow failed: %TARGET%

:done
echo.
pause
exit /b %EXIT_CODE%
