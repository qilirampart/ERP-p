# Print-ERP 故障排除指南

本文档记录了系统使用过程中的常见问题及解决方案。

---

## 🔴 严重问题（导致无法启动）

### 问题1: 登录时显示"网络错误，请检查网络连接" ⭐ 最常见

**原因**: **CORS配置问题** - 前端端口与后端CORS配置不匹配

**完整原理**:
- 浏览器的同源策略要求：协议、域名、端口都相同才能访问
- 前端(localhost:5174) 访问后端(localhost:8000) 属于跨域
- 后端必须在CORS配置中明确允许前端的URL
- 如果前端端口改变（5173→5174），但后端配置未更新，就会被拒绝

**症状**:
```
✅ 前端页面正常显示
✅ 可以看到登录表单
❌ 点击登录后提示"网络错误"
❌ 浏览器F12控制台显示: CORS policy blocked
```

**诊断步骤**:
```bash
# 1. 检查前端运行端口
# 查看前端启动日志，例如:
➜  Local:   http://localhost:5174/    # ← 记住这个端口

# 2. 检查后端是否运行
curl http://localhost:8000/
# 应该返回: {"message":"Print-ERP API Server",...}

# 3. 测试CORS
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:5174" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -i
# 查看响应头中的 access-control-allow-origin
```

**解决方案**:

1. 编辑 `backend/app/core/config.py` 第32行
2. 添加前端实际端口到CORS配置：
```python
# 修改前
BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

# 修改后
BACKEND_CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:5174",  # ← 添加你的实际端口
    "http://localhost:5175",  # ← 可以多添加几个备用
    "http://localhost:3000"
]
```

3. 保存文件，后端会自动重载（约2-3秒）
4. 刷新浏览器（Ctrl+F5）
5. 重新尝试登录

**预防措施**:
- 在CORS配置中预先添加多个常用端口（5173-5177）
- 使用固定端口启动前端：`npm run dev -- --port 5173`

---

### 问题2: 数据库连接失败

**错误信息**:
```
Can't connect to MySQL server on 'localhost'
sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server")
```

**原因**: MySQL服务未启动

**解决方案**:

**Windows (XAMPP用户)**:
1. 打开XAMPP控制面板
2. 找到MySQL行
3. 点击"Start"按钮
4. 等待变成绿色

**Windows (命令行)**:
```bash
# 启动MySQL服务
net start MySQL80

# 检查服务状态
sc query MySQL80
```

**Linux/Mac**:
```bash
# 启动MySQL
sudo systemctl start mysql

# 检查状态
sudo systemctl status mysql
```

**验证MySQL已启动**:
```bash
# 方式1: 使用命令行
mysql -u root -p

# 方式2: 检查端口
netstat -ano | grep 3306
# 应该看到: TCP  0.0.0.0:3306  ...  LISTENING
```

---

### 问题3: 数据库密码错误

**错误信息**:
```
Access denied for user 'root'@'localhost' (using password: YES)
```

**原因**: `.env` 文件中的数据库密码配置错误

**解决方案**:

1. 确认MySQL实际密码
2. 编辑 `backend/.env` 文件
3. 修改 `DATABASE_URL`:

```bash
# 有密码的情况
DATABASE_URL=mysql+aiomysql://root:你的密码@localhost:3306/print_erp?charset=utf8mb4

# 无密码的情况（XAMPP默认）
DATABASE_URL=mysql+aiomysql://root:@localhost:3306/print_erp?charset=utf8mb4
#                                  ↑ 注意这里是空的
```

4. 保存文件
5. 重启后端服务（Ctrl+C 然后重新运行）

---

## 🟡 中等问题（功能异常）

### 问题4: Alembic迁移失败

**错误信息**:
```
Target database is not up to date.
FAILED: Can't locate revision identified by 'xxxxx'
```

**原因**: 数据库版本与代码不同步

**解决方案**:

```bash
cd backend

# 1. 查看当前版本
poetry run alembic current

# 2. 查看所有可用版本
poetry run alembic history

# 3. 升级到最新版本
poetry run alembic upgrade head

# 4. 如果还是失败，重置数据库
# ⚠️ 警告：这会删除所有数据！
mysql -u root -p -e "DROP DATABASE print_erp; CREATE DATABASE print_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
poetry run alembic upgrade head
poetry run python scripts/init_db.py
```

---

### 问题5: 初始化数据失败（Duplicate entry）

**错误信息**:
```
IntegrityError: (1062, "Duplicate entry 'PAPER-001' for key 'ix_erp_materials_code'")
```

**原因**: 数据已经初始化过，再次运行 `init_db.py` 会冲突

**解决方案**:

**方案1: 跳过初始化（推荐）**
```bash
# 数据已存在，直接登录使用即可
# 用户名: admin, 密码: admin123
```

**方案2: 清空并重新初始化**
```bash
# ⚠️ 警告：这会删除所有数据！
mysql -u root -p

# 在MySQL中执行
DROP DATABASE print_erp;
CREATE DATABASE print_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 重新初始化
cd backend
poetry run alembic upgrade head
poetry run python scripts/init_db.py
```

---

### 问题6: 前端API请求404

**错误信息**:
```
GET http://localhost:8000/api/v1/materials/ 404 (Not Found)
```

**原因**:
1. 后端服务未启动
2. API路径错误
3. 路由未注册

**解决方案**:

```bash
# 1. 检查后端是否运行
curl http://localhost:8000/
# 应该返回: {"message":"Print-ERP API Server",...}

# 2. 检查API文档
# 访问 http://localhost:8000/docs
# 查看所有可用的API端点

# 3. 检查 frontend/.env 配置
cat frontend/.env
# 应该是: VITE_API_BASE_URL=http://localhost:8000

# 4. 清除浏览器缓存
# Ctrl+Shift+Delete → 清除缓存
# 或使用隐身模式测试
```

---

### 问题7: Token过期或无效

**错误信息**:
```
401 Unauthorized: Could not validate credentials
```

**原因**: JWT Token过期（默认30分钟）或无效

**解决方案**:

```bash
# 方案1: 重新登录获取新Token
# 在前端页面点击退出，然后重新登录

# 方案2: 修改Token过期时间
# 编辑 backend/.env
ACCESS_TOKEN_EXPIRE_MINUTES=60  # 改为60分钟

# 重启后端
```

---

## 🟢 轻微问题（体验优化）

### 问题8: 前端依赖安装慢

**症状**: `npm install` 非常慢或超时

**解决方案**:

```bash
cd frontend

# 方案1: 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install

# 方案2: 使用yarn
npm install -g yarn
yarn install

# 方案3: 使用pnpm（最快）
npm install -g pnpm
pnpm install
```

---

### 问题9: 后端Poetry安装慢

**症状**: `poetry install` 非常慢

**解决方案**:

```bash
cd backend

# 使用清华镜像
poetry source add --priority=default tsinghua https://pypi.tuna.tsinghua.edu.cn/simple/

# 重新安装
poetry install
```

---

### 问题10: 热重载不工作

**症状**: 修改代码后没有自动刷新

**后端热重载失败**:
```bash
# 确保使用了 --reload 参数
poetry run uvicorn app.main:app --reload --port 8000

# 检查是否有语法错误
# 后端控制台会显示错误信息
```

**前端热重载失败**:
```bash
# 重启前端服务
# Ctrl+C 停止
npm run dev

# 清除Vite缓存
rm -rf node_modules/.vite
npm run dev
```

---

## 🔍 诊断工具

### 检查系统状态

创建文件 `check_status.sh` (Linux/Mac) 或 `check_status.bat` (Windows):

**Windows (check_status.bat)**:
```batch
@echo off
echo === Print-ERP System Status Check ===
echo.

echo [1/5] Checking MySQL...
netstat -ano | findstr :3306
if %errorlevel% equ 0 (
    echo ✓ MySQL is running on port 3306
) else (
    echo ✗ MySQL is NOT running
)
echo.

echo [2/5] Checking Backend...
curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend is running on port 8000
) else (
    echo ✗ Backend is NOT running
)
echo.

echo [3/5] Checking Frontend...
netstat -ano | findstr :5173
if %errorlevel% equ 0 (
    echo ✓ Frontend is running on port 5173
) else (
    echo Frontend is NOT on 5173, checking 5174...
    netstat -ano | findstr :5174
    if %errorlevel% equ 0 (
        echo ✓ Frontend is running on port 5174
    ) else (
        echo ✗ Frontend is NOT running
    )
)
echo.

echo [4/5] Testing Backend API...
curl -s http://localhost:8000/api/v1/auth/login -X POST -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}" | findstr "登录成功"
if %errorlevel% equ 0 (
    echo ✓ Backend API is working
) else (
    echo ✗ Backend API test failed
)
echo.

echo [5/5] Checking Database Connection...
cd backend
poetry run python -c "from app.db.session import AsyncSessionLocal; import asyncio; asyncio.run(AsyncSessionLocal().__anext__())"
if %errorlevel% equ 0 (
    echo ✓ Database connection OK
) else (
    echo ✗ Database connection failed
)
cd ..

echo.
echo === Status Check Complete ===
pause
```

运行诊断:
```bash
# Windows
check_status.bat

# 或手动检查
netstat -ano | findstr ":3306 :8000 :5173 :5174"
```

---

## 📝 调试技巧

### 查看详细日志

**后端日志**:
```bash
# 启动时增加日志级别
poetry run uvicorn app.main:app --reload --port 8000 --log-level debug
```

**前端日志**:
- 打开浏览器开发者工具（F12）
- 查看 Console 标签
- 查看 Network 标签（查看API请求）

**数据库日志**:
```bash
# 编辑 backend/.env
DEBUG=True  # 启用SQL查询日志

# 后端控制台会显示所有SQL语句
```

---

### 使用Postman测试API

1. 下载安装 Postman
2. 创建新请求
3. 测试登录：
```
POST http://localhost:8000/api/v1/auth/login
Body (JSON):
{
  "username": "admin",
  "password": "admin123"
}
```
4. 复制返回的Token
5. 测试其他接口时，在Headers中添加：
```
Authorization: Bearer {你的token}
```

---

## 🆘 仍然无法解决？

### 收集诊断信息

运行以下命令收集信息：

```bash
# 系统信息
python --version
node --version
poetry --version

# 服务状态
netstat -ano | findstr ":3306 :8000 :5173"

# 后端日志
cd backend
poetry run uvicorn app.main:app --reload --port 8000 > backend.log 2>&1

# 前端日志
cd frontend
npm run dev > frontend.log 2>&1

# 检查数据库
mysql -u root -p -e "USE print_erp; SHOW TABLES;"
```

### 提交Issue

如果问题仍未解决，请提交Issue并包含：

1. **问题描述** - 详细描述问题
2. **复现步骤** - 如何触发这个问题
3. **错误信息** - 完整的错误日志
4. **环境信息** - OS版本、Python版本、Node版本
5. **截图** - 错误截图或浏览器控制台截图

---

## 📚 相关文档

- [QUICKSTART.md](QUICKSTART.md) - 快速启动指南
- [README.md](README.md) - 项目概览
- [backend/README.md](backend/README.md) - 后端文档
- [frontend/README.md](frontend/README.md) - 前端文档

---

**最后更新**: 2025-12-21
**维护者**: Print-ERP Team
