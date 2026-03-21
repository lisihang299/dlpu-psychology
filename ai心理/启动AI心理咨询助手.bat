@echo off
chcp 65001 > nul
title 大连工业大学 AI心理咨询助手 - 启动脚本

:: 切换到脚本所在目录（关键：确保bat和py文件同目录）
cd /d %~dp0

:: 检查Python是否安装
echo ==============================
echo 正在检查Python环境...
echo ==============================
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误：未检测到Python环境，请先安装Python 3.8+版本！
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python环境检测成功！

:: 安装/更新依赖包
echo.
echo ==============================
echo 正在安装/更新依赖包...
echo ==============================
pip install --upgrade pip > nul
pip install streamlit pysentiment2 python-dotenv openai pandas matplotlib > nul 2>&1
if errorlevel 1 (
    echo ⚠️  部分依赖安装失败，尝试手动安装：
    echo pip install streamlit pysentiment2 python-dotenv openai pandas matplotlib
    pause
) else (
    echo ✅ 依赖包安装完成！
)

:: 检查.env文件是否存在（可选）
if not exist ".env" (
    echo.
    echo ⚠️  未检测到.env文件！
    echo 请确保.env文件中配置了ZHIPU_API_KEY=你的智谱API密钥
    echo 按任意键继续（若无API密钥，运行时会报错）...
    pause > nul
)

:: 启动Streamlit应用
echo.
echo ==============================
echo 正在启动AI心理咨询助手...
echo 浏览器将自动打开，若未打开请访问：http://localhost:8501
echo ==============================
streamlit run ai_psychology_app.py

:: 防止窗口闪退（若启动失败可查看报错）
if errorlevel 1 (
    echo.
    echo ❌ 应用启动失败！
    pause
)