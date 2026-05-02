@echo off
setlocal enabledelayedexpansion

:: NebulaShell Smart Startup Script - Windows
cd /d "%~dp0"

:: Handle command line parameters
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="--version" goto :show_version
if "%1"=="-v" goto :show_version

echo.
echo  ========================================
echo    NebulaShell Startup Script - Windows
echo  ========================================
echo.

:: Check if an instance is already running
call :check_pid
if %errorlevel% neq 0 (
    echo [ERROR] An instance is already running, please stop it first
    pause
    exit /b 1
)

:: 1. Detect Python
echo [INFO] Detecting Python...

set "PYTHON_CMD="
for %%p in (python python3 py py3) do (
    where %%p >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=%%p"
        goto :found_python
    )
)

:found_python
if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python not found, please install Python 3.10+
    echo [TIP] Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set "PY_VER=%%i"
echo [SUCCESS] %PY_VER%

:: Display system info
echo [INFO] System Information:
echo   OS: Windows
echo   Working Directory: %CD%
echo   Time: %date% %time%

:: 2. Virtual Environment
echo.
echo [INFO] Configuring Python environment...

if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Cannot create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
) else (
    echo [SUCCESS] Virtual environment exists
)

call .venv\Scripts\activate.bat >nul 2>&1

:: 3. Install Dependencies
echo.
echo [INFO] Installing Python dependencies...

set "DEPS=click pyyaml websockets psutil cryptography"
set "TOTAL=5"
set "CURRENT=0"

for %%d in (%DEPS%) do (
    set /a CURRENT+=1
    call :printProgress !CURRENT! !TOTAL! "Installing %%d"
    
    %PYTHON_CMD% -c "import %%d" 2>nul
    if errorlevel 1 (
        pip install %%d -q 2>nul
    )
)

echo.
echo [SUCCESS] Python dependencies installed

:: Install project dependencies
if exist "pyproject.toml" (
    echo [INFO] Installing project configuration dependencies...
    pip install -e . -q 2>nul
)

if exist "requirements.txt" (
    echo [INFO] Installing requirements.txt...
    pip install -r requirements.txt -q 2>nul
)

:: 4. Check PHP
echo.
echo [INFO] Checking PHP...

where php >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PHP not installed, WebUI may not work properly
    echo [TIP] Install: choco install php or download from https://windows.php.net/download/
) else (
    for /f "tokens=*" %%i in ('php --version 2^>^&1 ^| findstr /r "PHP"') do set "PHP_VER=%%i"
    echo [SUCCESS] !PHP_VER!
)

:: 5. Create Data Directories
echo.
echo [INFO] Initializing data directories...

set "DIRS=data data\html-render data\web-toolkit data\plugin-storage data\DCIM data\pkg data\signature-verifier\keys\private data\signature-verifier\keys\public logs"

for %%d in (%DIRS%) do (
    if not exist "%%d" (
        mkdir "%%d" >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] Cannot create directory: %%d
        )
    )
)

echo [SUCCESS] Data directories ready

:: 6. Start Service
echo.
echo ========================================
echo   Starting NebulaShell
echo ========================================
echo.

:: Create PID file
call :create_pid "!random!"

if "%1"=="--daemon" goto :daemon_mode
if "%1"=="-d" goto :daemon_mode

:: Foreground mode
echo Running... Press Ctrl+C to stop
echo.

set "RESTART_DELAY=3"
set "RESTART_COUNT=0"
set "MAX_RESTARTS=10"

:loop
%PYTHON_CMD% -m oss.cli serve
set "EXIT_CODE=%errorlevel%"

if %EXIT_CODE% equ 0 (
    echo [SUCCESS] Service exited normally
    goto :end
)

:: Check if max restarts exceeded
if %RESTART_COUNT% geq %MAX_RESTARTS% (
    echo [ERROR] Reached maximum restart count (%MAX_RESTARTS%), stopping service
    goto :end
)

set /a RESTART_COUNT+=1
echo [WARNING] Service exited abnormally (code: %EXIT_CODE%), restarting in !RESTART_DELAY!s... (!RESTART_COUNT!/%MAX_RESTARTS%)
timeout /t !RESTART_DELAY! /nobreak >nul

:: Exponential backoff (max 60 seconds)
if !RESTART_DELAY! lss 60 (
    set /a RESTART_DELAY=!RESTART_DELAY! * 2
    if !RESTART_DELAY! gtr 60 set "RESTART_DELAY=60"
)

goto :loop

:daemon_mode
echo [WARNING] Windows daemon mode requires additional configuration
echo [TIP] Use Task Scheduler or nssm tool instead
echo.
echo [INFO] Starting background service...
start /b %PYTHON_CMD% -m oss.cli serve > logs\daemon.log 2>&1
goto :end

:end
call :cleanup
call .venv\Scripts\deactivate.bat >nul 2>&1
echo.
echo ========================================
echo   NebulaShell Stopped
echo ========================================
pause
exit /b 0

:: Progress bar function
:printProgress
set /a "pct=%1 * 100 / %2"
set /a "filled=pct / 2"
set /a "empty=50-filled"
set "bar="
for /l %%i in (1,1,%filled%) do set "bar=!bar!#"
for /l %%i in (1,1,%empty%) do set "bar=!bar!-"
echo   [!bar!] !pct!%% - %3
exit /b 0

:: Check if command exists
:command_exists
where %1 >nul 2>&1
exit /b %errorlevel%

:: Get current timestamp
:get_timestamp
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "T_DATE=%%c-%%a-%%b"
for /f "tokens=1-3 delims=: " %%a in ('time /t') do set "T_TIME=%%a:%%b:%%c"
set "TIMESTAMP=%T_DATE% %T_TIME%"
exit /b 0

:: Print separator
:print_separator
echo ========================================
exit /b 0

:: Health check
:health_check
set "check_url=%~1"
set "max_retries=%~2"
if "%max_retries%"=="" set "max_retries=30"
set "retry_count=0"

:health_loop
set /a retry_count+=1
curl -s "%check_url%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [HEALTH CHECK] Service is ready
    exit /b 0
)
if %retry_count% geq %max_retries% (
    echo [HEALTH CHECK] Service startup timeout
    exit /b 1
)
timeout /t 1 /nobreak >nul
goto :health_loop

:: Create PID file
:create_pid
echo %~1 > .pid
exit /b 0

:: Remove PID file
:remove_pid
if exist ".pid" del ".pid"
exit /b 0

:: Check PID file
:check_pid
if exist ".pid" (
    set /p PID=<.pid
    tasklist /fi "pid eq %PID%" 2>nul | find "%PID%" >nul
    if %errorlevel% equ 0 (
        echo [WARNING] Service already running (PID: %PID%)
        exit /b 1
    ) else (
        call :remove_pid
    )
)
exit /b 0

:: Show help information
:show_help
echo.
echo NebulaShell Startup Script - Windows Version
echo.
echo Usage: start.bat [options]
echo.
echo Options:
echo   --daemon, -d    Run in background mode (Windows recommends Task Scheduler)
echo   --help, -h      Show this help message
echo   --version, -v   Show version information
echo.
echo Examples:
echo   start.bat           Foreground mode
echo   start.bat --daemon  Background mode
echo.
exit /b 0

:: Show version information
:show_version
echo NebulaShell v1.0.0
echo Developer toolkit based on Python
echo.
exit /b 0

:: Cleanup function
:cleanup
echo [INFO] Cleaning up...
call :remove_pid
echo [SUCCESS] Cleanup completed
exit /b 0