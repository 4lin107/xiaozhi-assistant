@echo off
chcp 65001 >nul
REM AI语音助手Windows运行脚本

setlocal enabledelayedexpansion

REM 检查Python是否已安装
where python >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python 3.8或更高版本
    echo 您可以从以下链接下载Python:
    echo https://www.python.org/downloads/windows/
    echo 安装时请勾选"Add Python to PATH"选项
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set python_version=%%i
echo %python_version% 已安装

REM 检查pip是否已安装
where pip >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到pip，请确保Python安装时已包含pip
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('pip --version') do set pip_version=%%i
echo %pip_version% 已安装

REM 安装依赖
set "requirements_file=requirements.txt"
if exist %requirements_file% (
    echo 正在安装依赖...
    REM 先升级pip到最新版本以解决版本兼容性问题
    python -m pip install --upgrade pip
    if errorlevel 1 (
        echo pip升级失败，继续安装依赖...
    ) else (
        echo pip升级完成
    )
    
    REM 安装核心依赖（不包含spacy，避免numpy版本冲突）
    pip install SpeechRecognition pyaudio jieba nltk scikit-learn numpy pyttsx3 requests flask kivy kivymd pyside2 pymongo python-dotenv
    
    if errorlevel 1 (
        echo 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo 依赖安装完成
)

REM 运行带可视化窗口的语音助手
pythonw -c "from src.ui.simple_gui import main; main()"

REM 提示用户程序已启动
echo 语音助手已启动，可视化窗口正在运行...
echo 如果需要退出，请在可视化窗口中点击'退出'按钮，或在语音中说'退出'

pause