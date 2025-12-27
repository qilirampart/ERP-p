@echo off
echo ========================================
echo    Print-ERP 完全重启脚本
echo ========================================
echo.

echo [1/5] 停止所有服务...
echo 正在终止后端服务...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Print-ERP Backend*" 2>nul
taskkill /F /IM uvicorn.exe 2>nul

echo 正在终止前端服务...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Print-ERP Frontend*" 2>nul

timeout /t 2 /nobreak >nul
echo [✓] 服务已停止
echo.

echo [2/5] 清除前端构建缓存...
cd frontend
if exist node_modules\.vite (
    echo 删除 Vite 缓存...
    rd /s /q node_modules\.vite
)
if exist dist (
    echo 删除 dist 目录...
    rd /s /q dist
)
cd ..
echo [✓] 前端缓存已清除
echo.

echo [3/5] 启动后端服务...
start "Print-ERP Backend" cmd /k "cd /d %cd%\backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak >nul
echo [✓] 后端服务已启动
echo.

echo [4/5] 启动前端服务...
start "Print-ERP Frontend" cmd /k "cd /d %cd%\frontend && npm run dev"
timeout /t 8 /nobreak >nul
echo [✓] 前端服务已启动
echo.

echo [5/5] 打开清除缓存页面...
start clear-cache.html
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   重启完成！
echo ========================================
echo.
echo 提示：
echo 1. 浏览器已打开清除缓存页面
echo 2. 请点击"清除缓存数据"按钮
echo 3. 然后使用 admin/admin123 登录
echo.
echo 后端:  http://localhost:8000
echo 前端:  http://localhost:5173
echo.
pause
