@echo off
REM 印刷ERP系统 - Windows快速部署脚本

echo =========================================
echo   印刷ERP系统 - Docker快速部署
echo =========================================
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    echo    下载地址: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo ✅ Docker已安装
echo.

REM 检查.env文件
if not exist .env (
    echo ⚠️  未找到.env文件，正在创建...
    copy .env.example .env
    echo ✅ 已创建.env文件，请编辑文件并配置密码
    echo.
    echo 按任意键继续编辑.env文件...
    pause >nul
    notepad .env
) else (
    echo ✅ .env文件已存在
)

echo.
echo 选择部署方式：
echo   1) 快速启动（使用现有镜像）
echo   2) 完整构建（重新构建所有镜像）
echo.
set /p choice="请选择 [1-2]: "

if "%choice%"=="1" (
    echo.
    echo 🚀 正在启动服务...
    docker compose up -d
) else if "%choice%"=="2" (
    echo.
    echo 🔨 正在构建镜像...
    docker compose build --no-cache
    echo.
    echo 🚀 正在启动服务...
    docker compose up -d
) else (
    echo 无效选择
    pause
    exit /b 1
)

echo.
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo.
echo 📊 服务状态：
docker compose ps

echo.
echo =========================================
echo   ✅ 部署完成！
echo =========================================
echo.
echo 访问地址：
echo   前端界面: http://localhost
echo   后端API:  http://localhost:8000
echo   API文档:  http://localhost:8000/docs
echo.
echo 默认管理员账号：
echo   用户名: admin
echo   密码:   admin123
echo.
echo ⚠️  首次登录后请立即修改密码！
echo.
echo 常用命令：
echo   查看日志:  docker compose logs -f
echo   停止服务:  docker compose down
echo   重启服务:  docker compose restart
echo.
pause
