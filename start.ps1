# Print-ERP System 一键启动脚本 (PowerShell)
# 使用方法: 右键 -> 使用PowerShell运行

$ErrorActionPreference = "Stop"

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Print-ERP System 一键启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取脚本所在目录
$scriptDir = $PSScriptRoot
if (-not $scriptDir) {
    $scriptDir = Get-Location
}

# 检查目录
if (-not (Test-Path "$scriptDir\backend")) {
    Write-Host "[错误] 未找到backend目录" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

if (-not (Test-Path "$scriptDir\frontend")) {
    Write-Host "[错误] 未找到frontend目录" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 函数: 检查端口是否被占用
function Test-PortInUse {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connections
}

# 检查端口占用
Write-Host "[1/5] 检查端口占用..." -ForegroundColor Yellow
$backendPort = 8000
$frontendPort = 5173

if (Test-PortInUse -Port $backendPort) {
    Write-Host "[警告] 端口 $backendPort 已被占用，后端可能无法启动" -ForegroundColor Yellow
    $continue = Read-Host "是否继续? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 0
    }
}

if (Test-PortInUse -Port $frontendPort) {
    Write-Host "[警告] 端口 $frontendPort 已被占用，前端可能无法启动" -ForegroundColor Yellow
    $continue = Read-Host "是否继续? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 0
    }
}

Write-Host "[✓] 端口检查完成" -ForegroundColor Green
Write-Host ""

# 检查后端依赖
Write-Host "[2/5] 检查后端环境..." -ForegroundColor Yellow
if (-not (Test-Path "$scriptDir\backend\pyproject.toml")) {
    Write-Host "[错误] 未找到 pyproject.toml" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 检查Poetry是否安装
$poetryInstalled = $null -ne (Get-Command poetry -ErrorAction SilentlyContinue)
if (-not $poetryInstalled) {
    Write-Host "[错误] 未找到Poetry，请先安装Poetry" -ForegroundColor Red
    Write-Host "安装方法: pip install poetry" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

Write-Host "[✓] 后端环境检查完成" -ForegroundColor Green
Write-Host ""

# 检查前端依赖
Write-Host "[3/5] 检查前端环境..." -ForegroundColor Yellow
if (-not (Test-Path "$scriptDir\frontend\package.json")) {
    Write-Host "[错误] 未找到 package.json" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

if (-not (Test-Path "$scriptDir\frontend\node_modules")) {
    Write-Host "[警告] 未找到 node_modules，建议先运行 'npm install'" -ForegroundColor Yellow
}

Write-Host "[✓] 前端环境检查完成" -ForegroundColor Green
Write-Host ""

# 启动后端
Write-Host "[4/5] 启动后端服务..." -ForegroundColor Yellow
$backendCmd = "cd '$scriptDir\backend'; Write-Host '[后端] 正在启动FastAPI服务...' -ForegroundColor Green; poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Write-Host "[✓] 后端服务启动中 (端口: 8000)" -ForegroundColor Green
Start-Sleep -Seconds 3

# 启动前端
Write-Host "[5/5] 启动前端服务..." -ForegroundColor Yellow
$frontendCmd = "cd '$scriptDir\frontend'; Write-Host '[前端] 正在启动Vite开发服务器...' -ForegroundColor Green; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "[✓] 前端服务启动中 (端口: 5173)" -ForegroundColor Green
Write-Host ""

# 等待服务启动并打开浏览器
Write-Host "[6/6] 等待服务启动完成..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host "正在打开浏览器..." -ForegroundColor Green
Start-Process "http://localhost:5173"

# 完成提示
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后端服务: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Blue
Write-Host "API文档:  " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "前端服务: " -NoNewline
Write-Host "http://localhost:5173 " -ForegroundColor Blue -NoNewline
Write-Host "(已自动打开)" -ForegroundColor Green
Write-Host ""
Write-Host "提示: 两个PowerShell窗口已打开，关闭窗口即可停止服务" -ForegroundColor Yellow
Write-Host "      浏览器应该已自动打开，如未打开请手动访问上述地址" -ForegroundColor Yellow
Write-Host ""

Read-Host "按Enter键关闭此窗口"
