@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ═══════════════════════════════════════════════════════════
::  FutureOSS 智能启动脚本 - Windows
::  自动检测环境 / 安装依赖 / 进度显示 / 守护重启
:: ═══════════════════════════════════════════════════════════

cd /d "%~dp0"

:: ── 处理命令行参数 ──
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="--version" goto :show_version
if "%1"=="-v" goto :show_version

:: ── 颜色代码 ──
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
    set "DEL=%%a"
)

:: ── 工具函数 ──
call :colorEcho 0B "[信息] 环境检测中..."
call :colorEcho 0A "[成功] 检测完成"
call :colorEcho 0E "[警告] 某些组件缺失"
call :colorEcho 0C "[错误] 检测失败"

:: ── Logo ──
echo.
call :colorEcho 0B " ███████╗ ██████╗  ██████╗  ██████╗ ██████╗  ██████╗ "
call :colorEcho 0B " ██╔════╝ ██╔══██╗ ██╔══██╗ ██╔══██╗ ██╔══██╗██╔════╝ "
call :colorEcho 0B " █████╗   ██████╔╝ ██████╔╝ ██████╔╝ ██║  ██║██║  ███╗"
call :colorEcho 0B " ██╔══╝   ██╔══██╗ ██╔══██╗ ██╔══██╗ ██║  ██║██║   ██║"
call :colorEcho 0B " ██║      ██║  ██║ ██║  ██║ ██║  ██║ ██████╔╝╚██████╔╝"
call :colorEcho 0B " ╚═╝      ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ "
echo.
call :colorEcho 0F "         开发者通用工具套组 · 一切皆为插件"
call :colorEcho 07 "         https://gitee.com/starlight-apk/feature-oss"
echo.

:: ── 检查是否已有实例在运行 ──
call :check_pid
if %errorlevel% neq 0 (
    call :colorEcho 0C "[错误] 检测到已有实例在运行，请先停止"
    pause
    exit /b 1
)

:: ═══════════════════════════════════════════════════════════
::  1. 检测 Python
:: ═══════════════════════════════════════════════════════════
call :colorEcho 0B "[信息] 检测 Python..."

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
    call :colorEcho 0C "[错误] 未找到 Python，请先安装 Python 3.10+"
    call :colorEcho 0E "[提示] 下载地址: https://www.python.org/downloads/"
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set "PY_VER=%%i"
call :colorEcho 0A "[成功] %PY_VER%"

:: 显示系统信息
call :colorEcho 0B "[信息] 系统信息:"
echo   OS: Windows
echo   工作目录: %CD%
echo   时间: %date% %time%

:: ═══════════════════════════════════════════════════════════
::  2. 虚拟环境
:: ═══════════════════════════════════════════════════════════
echo.
call :colorEcho 0B "[信息] 配置 Python 环境..."

if not exist ".venv" (
    call :colorEcho 0E "[信息] 创建虚拟环境..."
    %PYTHON_CMD% -m venv .venv >nul 2>&1
    if errorlevel 1 (
        call :colorEcho 0C "[错误] 无法创建虚拟环境"
        pause
        exit /b 1
    )
    call :colorEcho 0A "[成功] 虚拟环境已创建"
) else (
    call :colorEcho 0A "[成功] 虚拟环境已存在"
)

call .venv\Scripts\activate.bat >nul 2>&1

:: ═══════════════════════════════════════════════════════════
::  3. 安装依赖
:: ═══════════════════════════════════════════════════════════
echo.
call :colorEcho 0B "[信息] 安装 Python 依赖..."

set "DEPS=click pyyaml websockets psutil cryptography"
set "TOTAL=5"
set "CURRENT=0"

for %%d in (%DEPS%) do (
    set /a CURRENT+=1
    call :printProgress !CURRENT! !TOTAL! "安装 %%d"
    
    %PYTHON_CMD% -c "import %%d" 2>nul
    if errorlevel 1 (
        pip install %%d -q 2>nul
    )
)

echo.
echo.
call :colorEcho 0A "[成功] Python 依赖安装完成"

:: 安装项目依赖
if exist "pyproject.toml" (
    call :colorEcho 0E "[信息] 安装项目配置依赖..."
    pip install -e . -q 2>nul
)

if exist "requirements.txt" (
    call :colorEcho 0E "[信息] 安装 requirements.txt..."
    pip install -r requirements.txt -q 2>nul
)

:: ═══════════════════════════════════════════════════════════
::  4. 检查 PHP
:: ═══════════════════════════════════════════════════════════
echo.
call :colorEcho 0B "[信息] 检查 PHP..."

where php >nul 2>&1
if errorlevel 1 (
    call :colorEcho 0E "[警告] PHP 未安装，WebUI 可能无法正常工作"
    call :colorEcho 07 "[提示] 安装: choco install php 或从 https://windows.php.net/download/ 下载"
) else (
    for /f "tokens=*" %%i in ('php --version 2^>^&1 ^| findstr /r "PHP"') do set "PHP_VER=%%i"
    call :colorEcho 0A "[成功] !PHP_VER!"
)

:: ═══════════════════════════════════════════════════════════
::  5. 创建数据目录
:: ═══════════════════════════════════════════════════════════
echo.
call :colorEcho 0B "[信息] 初始化数据目录..."

set "DIRS=data data\html-render data\web-toolkit data\plugin-storage data\DCIM data\pkg data\signature-verifier\keys\private data\signature-verifier\keys\public logs"

for %%d in (%DIRS%) do (
    if not exist "%%d" (
        mkdir "%%d" >nul 2>&1
        if errorlevel 1 (
            call :colorEcho 0C "[错误] 无法创建目录: %%d"
        )
    )
)

call :colorEcho 0A "[成功] 数据目录已就绪"

:: ═══════════════════════════════════════════════════════════
::  6. 启动服务
:: ═══════════════════════════════════════════════════════════
echo.
call :colorEcho 0B "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
call :colorEcho 0B "  启动 FutureOSS"
call :colorEcho 0B "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo.

:: 创建 PID 文件
call :create_pid "!random!"

if "%1"=="--daemon" goto :daemon_mode
if "%1"=="-d" goto :daemon_mode

:: 前台模式
call :colorEcho 0F "运行中... 按 Ctrl+C 停止"
echo.

set "RESTART_DELAY=3"
set "RESTART_COUNT=0"
set "MAX_RESTARTS=10"

:loop
%PYTHON_CMD% -m oss.cli serve
set "EXIT_CODE=%errorlevel%"

if %EXIT_CODE% equ 0 (
    call :colorEcho 0A "[成功] 服务正常退出"
    goto :end
)

:: 检查是否超过最大重启次数
if %RESTART_COUNT% geq %MAX_RESTARTS% (
    call :colorEcho 0C "[错误] 达到最大重启次数 (%MAX_RESTARTS%)，停止服务"
    goto :end
)

set /a RESTART_COUNT+=1
call :colorEcho 0E "[警告] 服务异常退出 (code: %EXIT_CODE%)，!RESTART_DELAY!s 后重启... (第 !RESTART_COUNT!/%MAX_RESTARTS% 次)"
timeout /t !RESTART_DELAY! /nobreak >nul

:: 指数退避 (最大 60 秒)
if !RESTART_DELAY! lss 60 (
    set /a RESTART_DELAY=!RESTART_DELAY! * 2
    if !RESTART_DELAY! gtr 60 set "RESTART_DELAY=60"
)

goto :loop

:daemon_mode
call :colorEcho 0E "[警告] Windows 守护模式需要额外配置"
call :colorEcho 07 "[提示] 建议使用任务计划程序或 nssm 工具实现"
echo.
call :colorEcho 0B "[信息] 启动后台服务..."
start /b %PYTHON_CMD% -m oss.cli serve > logs\daemon.log 2>&1
goto :end

:end
call :cleanup
call .venv\Scripts\deactivate.bat >nul 2>&1
echo.
call :colorEcho 0B "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
call :colorEcho 0F "  FutureOSS 已停止"
call :colorEcho 0B "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pause
exit /b 0

:: ── 进度条函数 ──
:printProgress
set /a "pct=%1 * 100 / %2"
set /a "filled=pct / 2"
set /a "empty=50-filled"
set "bar="
for /l %%i in (1,1,%filled%) do set "bar=!bar!█"
for /l %%i in (1,1,%empty%) do set "bar=!bar!░"
echo   [!bar!] !pct!%% - %3
exit /b 0

:: ── 颜色输出函数 ──
:colorEcho
set "params=%1"
set "msg=%~2"
call :colorText %params% "%msg%"
exit /b 0

:colorText
<nul set /p "=%DEL%"
findstr /v /a:%1 /R "^$" "%DEL%" nul
<nul set /p "=%DEL%%DEL%%DEL%%DEL%%DEL%%DEL%%DEL%"
echo %~2
exit /b 0

:: ── 检查命令是否存在 ──
:command_exists
where %1 >nul 2>&1
exit /b %errorlevel%

:: ── 获取当前时间戳 ──
:get_timestamp
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "T_DATE=%%c-%%a-%%b"
for /f "tokens=1-3 delims=: " %%a in ('time /t') do set "T_TIME=%%a:%%b:%%c"
set "TIMESTAMP=%T_DATE% %T_TIME%"
exit /b 0

:: ── 打印分隔线 ──
:print_separator
echo ═══════════════════════════════════════════════════════════
exit /b 0

:: ── 打印带颜色的状态 ──
:print_status
set "status_type=%~1"
set "status_msg=%~2"
if "%status_type%"=="info" call :colorEcho 0B "[信息] %status_msg%"
if "%status_type%"=="success" call :colorEcho 0A "[成功] %status_msg%"
if "%status_type%"=="warn" call :colorEcho 0E "[警告] %status_msg%"
if "%status_type%"=="error" call :colorEcho 0C "[错误] %status_msg%"
exit /b 0

:: ── 健康检查 ──
:health_check
set "check_url=%~1"
set "max_retries=%~2"
if "%max_retries%"=="" set "max_retries=30"
set "retry_count=0"

:health_loop
set /a retry_count+=1
curl -s "%check_url%" >nul 2>&1
if %errorlevel% equ 0 (
    call :colorEcho 0A "[健康检查] 服务已就绪"
    exit /b 0
)
if %retry_count% geq %max_retries% (
    call :colorEcho 0C "[健康检查] 服务启动超时"
    exit /b 1
)
timeout /t 1 /nobreak >nul
goto :health_loop

:: ── 创建 PID 文件 ──
:create_pid
echo %~1 > .pid
exit /b 0

:: ── 删除 PID 文件 ──
:remove_pid
if exist ".pid" del ".pid"
exit /b 0

:: ── 检查 PID 文件 ──
:check_pid
if exist ".pid" (
    set /p PID=<.pid
    tasklist /fi "pid eq %PID%" 2>nul | find "%PID%" >nul
    if %errorlevel% equ 0 (
        call :colorEcho 0E "[警告] 服务已在运行 (PID: %PID%)"
        exit /b 1
    ) else (
        call :remove_pid
    )
)
exit /b 0

:: ── 显示帮助信息 ──
:show_help
echo.
call :colorEcho 0F "FutureOSS 启动脚本 - Windows 版本"
echo.
echo 用法: start.bat [选项]
echo.
echo 选项:
echo   --daemon, -d    以后台模式运行（Windows 建议使用任务计划程序）
echo   --help, -h      显示此帮助信息
echo   --version, -v   显示版本信息
echo.
echo 示例:
echo   start.bat           前台运行模式
echo   start.bat --daemon  后台运行模式
echo.
exit /b 0

:: ── 显示版本信息 ──
:show_version
echo FutureOSS v1.0.0
echo 基于 Python 的开发者通用工具套组
echo.
exit /b 0

:: ── 清理函数 ──
:cleanup
call :colorEcho 0E "[信息] 正在清理..."
call :remove_pid
call :colorEcho 0A "[成功] 清理完成"
exit /b 0