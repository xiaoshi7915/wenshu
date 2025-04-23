@echo off
echo === WenShu 自然语言数据库查询智能体 ===
echo 正在准备启动环境...

:: 检查Python版本
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python
    echo 请安装Python 3.10+后重试
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo 检测到 Python %python_version%

:: 检查虚拟环境
if not exist venv (
    echo 未检测到虚拟环境，正在创建...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
) else (
    echo 检测到现有虚拟环境
)

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 激活虚拟环境失败
    pause
    exit /b 1
)

:: 安装依赖
echo 检查依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 安装依赖失败
    pause
    exit /b 1
)
echo 依赖安装完成

:: 检查.env文件
if not exist .env (
    echo 未检测到.env文件，使用示例配置...
    copy .env.example .env > nul
    echo .env文件创建成功
) else (
    echo 检测到.env文件
)

:: 启动应用
echo 正在启动WenShu应用...
echo 应用将在 http://localhost:5000 上运行
echo 按Ctrl+C可停止应用
python run.py 