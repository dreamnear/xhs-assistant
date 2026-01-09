@echo off
REM ========================================
REM 小红书数据抓取工具 - Windows打包脚本
REM ========================================

echo.
echo ========================================
echo 小红书数据抓取工具 - Windows打包脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo [1/6] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)

echo [2/6] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/6] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

echo [4/6] 安装Playwright浏览器...
playwright install chromium
if errorlevel 1 (
    echo [错误] 安装浏览器失败
    pause
    exit /b 1
)

echo [5/6] 开始打包...
pyinstaller build/windows.spec --clean
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo [6/6] 复制Playwright浏览器到dist目录...
if exist "dist\小红书数据抓取工具" (
    xcopy /E /I /Y venv\Lib\site-packages\playwright\driver "dist\小红书数据抓取工具\playwright\driver"
    xcopy /E /I /Y venv\Lib\site-packages\playwright\driver\package\playwright\driver "dist\小红书数据抓取工具\playwright\driver\package\playwright\driver"
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\小红书数据抓取工具.exe
echo.
echo 注意：
echo 1. 首次运行会自动创建必要的目录
echo 2. 会话文件保存在程序目录下的.sessions文件夹
echo 3. 导出数据保存在程序目录下的data/output文件夹
echo.
pause
