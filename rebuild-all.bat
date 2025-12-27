@echo off
chcp 65001 >nul
echo ========================================
echo    Print-ERP 完全重建脚本
echo ========================================
echo.

echo [1/7] 停止所有服务...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 3 /nobreak >nul
echo [✓] 所有服务已停止
echo.

echo [2/7] 清除前端所有缓存和构建文件...
cd frontend
if exist node_modules\.vite (
    echo 删除 Vite 缓存...
    rd /s /q node_modules\.vite
)
if exist dist (
    echo 删除 dist 目录...
    rd /s /q dist
)
if exist .vite (
    echo 删除 .vite 目录...
    rd /s /q .vite
)
cd ..
echo [✓] 前端缓存已清除
echo.

echo [3/7] 启动后端服务...
start "Print-ERP Backend" cmd /k "cd /d %cd%\backend && echo 后端服务启动中... && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo 等待后端启动（10秒）...
timeout /t 10 /nobreak >nul
echo [✓] 后端服务已启动
echo.

echo [4/7] 启动前端服务（完全重新编译）...
start "Print-ERP Frontend" cmd /k "cd /d %cd%\frontend && echo 前端服务启动中... && npm run dev -- --force"
echo 等待前端编译（15秒）...
timeout /t 15 /nobreak >nul
echo [✓] 前端服务已启动
echo.

echo [5/7] 测试后端API...
curl -s http://localhost:8000/health >nul
if %errorlevel% equ 0 (
    echo [✓] 后端API正常响应
) else (
    echo [!] 后端API未响应，请检查后端窗口
)
echo.

echo [6/7] 打开强制清除缓存页面...
start force-clear-cache.html
timeout /t 2 /nobreak >nul
echo [✓] 清除缓存页面已打开
echo.

echo [7/7] 完成！
echo.
echo ========================================
echo   重建完成！
echo ========================================
echo.
echo 📋 接下来请按照以下步骤操作：
echo.
echo 1. 在打开的清除缓存页面中，点击"强制清除所有缓存"
echo 2. 关闭浏览器（完全退出，查看任务栏）
echo 3. 重新打开浏览器
echo 4. 访问: http://localhost:5173
echo 5. 按住 Ctrl+Shift+R 强制刷新页面
echo 6. 应该会看到登录页面
echo.
echo 后端:  http://localhost:8000
echo 前端:  http://localhost:5173
echo.
echo ⚠️  如果仍然直接跳转到仪表板：
echo    1. 按 F12 打开开发者工具
echo    2. 在 Console 输入: localStorage.clear(); location.reload()
echo    3. 按 Enter 执行
echo.
pause
