# 印刷ERP系统 - PowerShell部署脚本

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  印刷ERP系统 - Docker快速部署" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker是否安装
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker未安装，请先安装Docker Desktop" -ForegroundColor Red
    Write-Host "   下载地址: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host ""

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  未找到.env文件，正在创建..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ 已创建.env文件" -ForegroundColor Green
    Write-Host ""
    Write-Host "请编辑.env文件并配置密码..." -ForegroundColor Yellow
    Read-Host "按Enter键继续编辑.env文件"
    notepad .env
} else {
    Write-Host "✅ .env文件已存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "选择部署方式：" -ForegroundColor Cyan
Write-Host "  1) 快速启动（使用现有镜像）"
Write-Host "  2) 完整构建（重新构建所有镜像）"
Write-Host ""

$choice = Read-Host "请选择 [1-2]"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "🚀 正在启动服务..." -ForegroundColor Green
    docker compose up -d
} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "🔨 正在构建镜像..." -ForegroundColor Yellow
    docker compose build --no-cache
    Write-Host ""
    Write-Host "🚀 正在启动服务..." -ForegroundColor Green
    docker compose up -d
} else {
    Write-Host "❌ 无效选择" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host ""
Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host ""
Write-Host "📊 服务状态：" -ForegroundColor Cyan
docker compose ps

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  ✅ 部署完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址：" -ForegroundColor Cyan
Write-Host "  前端界面: http://localhost"
Write-Host "  后端API:  http://localhost:8000"
Write-Host "  API文档:  http://localhost:8000/docs"
Write-Host ""
Write-Host "默认管理员账号：" -ForegroundColor Yellow
Write-Host "  用户名: admin"
Write-Host "  密码:   admin123"
Write-Host ""
Write-Host "⚠️  首次登录后请立即修改密码！" -ForegroundColor Red
Write-Host ""
Write-Host "常用命令：" -ForegroundColor Cyan
Write-Host "  查看日志:  docker compose logs -f"
Write-Host "  停止服务:  docker compose down"
Write-Host "  重启服务:  docker compose restart"
Write-Host ""

Read-Host "按Enter键退出"
