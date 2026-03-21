@echo off
chcp 65001 >nul
echo ==============================================
echo          心理测评工具 - 一键打包脚本
echo ==============================================
echo.

:: 切换到脚本所在的根文件夹（关键！）
cd /d "%~dp0"

echo 🔧 第一步：删除旧打包文件...
rd /s /q build 2>nul
rd /s /q dist 2>nul
del /f 心理测评工具.spec 2>nul

echo 🔧 第二步：安装/更新依赖...
pip install pyinstaller streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ❌ 依赖安装失败！请检查Python是否添加到系统PATH。
    pause
    exit /b 1
)
echo ✅ 依赖安装完成！
echo.

echo 🔧 第三步：开始打包EXE...
pyinstaller --onefile --windowed ^
--hidden-import=streamlit ^
--hidden-import=streamlit.runtime.scriptrunner.magic_funcs ^
--additional-hooks-dir=. ^
--name="心理测评工具" ^
ai_psychology_app.py

if errorlevel 1 (
    echo ❌ 打包失败！请检查：
    echo    1. 主代码文件名是否为 ai_psychology_app.py
    echo    2. 代码是否有语法错误
    pause
    exit /b 1
)

echo ✅ 打包成功！
echo 📂 EXE文件位置：%~dp0\dist\心理测评工具.exe
echo ⚠️  提示：首次运行EXE会慢，杀毒软件误报请添加信任。
echo.
echo 按任意键关闭...
pause >nul