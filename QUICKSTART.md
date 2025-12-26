# Print-ERP 快速启动指南

本指南将帮助你在 **5分钟内** 启动整个系统，包含完整的故障排除方案。

---

## 📋 前置条件检查

在开始之前，请确保已安装：

- ✅ Python 3.10+ (`python --version`)
- ✅ Node.js 18+ (`node --version`)
- ✅ MySQL 8.0 (运行中)
- ✅ Poetry (`poetry --version`)

---

## 🚀 快速启动步骤

### 第1步: 准备数据库

#### 方式1: 使用MySQL命令行

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE print_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### 方式2: 使用XAMPP（Windows推荐）

1. 启动XAMPP控制面板
2. 确保MySQL服务已启动（绿色按钮）
3. 数据库会自动可用

### 第2步: 启动后端服务

```bash
# 进入后端目录
cd backend

# 安装依赖（首次运行）
poetry install

# 配置环境变量
cp .env.example .env

# 编辑 .env 文件，修改数据库连接
# DATABASE_URL=mysql+aiomysql://root:你的密码@localhost:3306/print_erp?charset=utf8mb4
# 注意：如果MySQL没有密码，格式为: root:@localhost

# 执行数据库迁移
poetry run alembic upgrade head

# 初始化数据（创建账号和示例数据）
poetry run python scripts/init_db.py

# 启动后端服务
poetry run uvicorn app.main:app --reload --port 8000
```

✅ **后端启动成功标志**：
- 控制台显示: `Application startup complete.`
- 访问 http://localhost:8000 看到欢迎信息
- 访问 http://localhost:8000/docs 查看API文档

### 第3步: 启动前端服务

**⚠️ 重要：请打开新终端窗口执行**

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

✅ **前端启动成功标志**：
- 控制台显示: `Local: http://localhost:5173/`
- 或显示: `Local: http://localhost:5174/` （如果5173被占用）

**📝 记住你的前端端口号！后面会用到。**

---

## ⚠️ 重要：端口与CORS配置问题

### 问题描述

如果你看到登录页面显示 **"网络错误，请检查网络连接"**，这通常是因为：

1. **前端端口不是5173** - Vite可能因为端口占用而使用5174或其他端口
2. **后端CORS未配置** - 后端默认只允许5173端口访问

### 解决方案

#### 步骤1: 确认前端实际端口

检查前端启动时的输出：
```bash
# 输出示例
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5174/    # ← 这是实际端口！
➜  Network: use --host to expose
```

#### 步骤2: 修改后端CORS配置

如果前端端口**不是5173**，需要修改后端配置：

编辑文件：`backend/app/core/config.py`

找到第32行（CORS配置）：
```python
# 修改前
BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

# 修改后（添加你的实际端口）
BACKEND_CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:5174",  # ← 添加实际端口
    "http://localhost:3000"
]
```

#### 步骤3: 后端自动重载

保存文件后，Uvicorn会自动重载配置（约2-3秒）：
```bash
# 后端控制台显示
WARNING:  WatchFiles detected changes in 'app\core\config.py'. Reloading...
INFO:     Application startup complete.
```

#### 步骤4: 刷新浏览器

返回浏览器，刷新页面（Ctrl+F5 强制刷新），现在应该可以登录了！

---

## 🎯 登录测试

打开浏览器访问前端地址（根据实际端口）：
- **http://localhost:5173** 或
- **http://localhost:5174**

使用以下账号登录：

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 完全权限 |
| 销售 | sales | sales123 | 报价、订单 |
| 操作员 | operator | operator123 | 生产管理 |

---

## ✅ 功能测试清单

### 1. 测试物料管理 🏷️

1. 点击左侧导航 **库存管理**
2. 查看系统已初始化的 8 个物料：
   - 5种纸张（双铜纸157g/200g/250g、哑粉纸157g、特种纸300g）
   - 2种油墨（四色油墨套装）
   - 1种辅料（哑膜、亮膜）
3. 点击 **入库** 按钮，测试入库功能：
   - 物料: 双铜纸 157g
   - 数量: 2
   - 单位: 令
   - 提交后，库存应增加 **1000张**（2令 × 500张/令）

**验证点**：
- ✅ 单位自动换算正确
- ✅ 库存数量更新
- ✅ 低库存预警（<500张显示红色，500-2000黄色）

### 2. 测试智能报价 💰 ⭐ 核心功能

1. 点击左侧导航 **智能报价计算**
2. 填写产品规格：
   - **选择纸张**: 双铜纸 157g - 787×1092mm
   - **成品尺寸**: 210 × 285 mm (A4尺寸)
   - **印数**: 5000
   - **页数**: 4
   - **修边尺寸**: 10mm（可选）
3. 选择工艺（可选）：
   - 覆膜：哑膜
   - 装订：骑马钉
4. 点击 **智能计算报价** 按钮
5. 查看右侧报价卡片：

**预期结果**：
```
开纸方案：横切（旋转90°）
开数：10 开
纸张利用率：54.6% (良)

纸张消耗：1000 张
纸张成本：¥350.00
印刷工费：¥1000.00
工艺费用：¥150.00
━━━━━━━━━━━━━━━━
总成本：¥1500.00
```

**验证点**：
- ✅ 自动计算直切和横切两种方案
- ✅ 选择开数更大的方案
- ✅ 利用率计算准确
- ✅ 成本明细清晰

### 3. 测试仪表盘 📊

1. 点击左侧导航 **仪表盘**
2. 查看统计卡片：
   - 今日订单
   - 生产工单
   - 库存预警
   - 本月营收
3. 点击快速操作按钮：
   - 新建订单
   - 库存入库
   - 数据报表

**注意**: 仪表盘数据为模拟数据，实际使用需连接真实API。

### 4. 测试API接口 📡

访问 **http://localhost:8000/docs** （Swagger UI）

尝试以下接口：

1. **POST /api/v1/auth/login** - 登录获取Token
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```

2. **GET /api/v1/materials/** - 获取物料列表
   - 需要在请求头添加 Token：`Bearer {token}`

3. **POST /api/v1/quotes/calculate** - 计算报价
   ```json
   {
     "paper_id": 1,
     "target_w": 210,
     "target_h": 285,
     "quantity": 5000,
     "page_count": 4
   }
   ```

---

## 🎨 UI/UX 特色体验

本系统采用 **Modern Bento Grid** 设计：

- 🎯 **大圆角卡片** - 24px圆角，现代感十足
- 💎 **Indigo配色** - #4F46E5 主色，Linear风格
- ✨ **悬浮动效** - 卡片hover时轻微上浮（translateY -2px）
- 🌈 **通透质感** - 磨砂玻璃效果
- 📊 **数字等宽** - Inter字体，金额显示清晰
- 🎭 **渐变按钮** - Indigo渐变，视觉焦点明确
- 📏 **扁平输入框** - 简洁现代，focus时显示ring动画

---

## 🐛 常见问题与解决方案

### 问题1: 登录时显示"网络错误，请检查网络连接"

**原因**: CORS配置问题，前端端口与后端配置不一致

**症状**:
- 前端页面正常显示
- 点击登录按钮后提示网络错误
- 浏览器控制台显示 `CORS Error` 或 `Network Error`

**解决方案**: 参考上面 [⚠️ 端口与CORS配置问题](#-重要端口与cors配置问题) 章节

**快速检查**:
```bash
# 1. 检查前端端口
# 查看前端启动日志，确认端口号

# 2. 检查后端CORS配置
# 编辑 backend/app/core/config.py
# 确保 BACKEND_CORS_ORIGINS 包含前端端口

# 3. 测试后端是否响应
curl http://localhost:8000/
# 应该返回: {"message":"Print-ERP API Server",...}
```

### 问题2: 数据库连接失败

**错误信息**: `Can't connect to MySQL server` 或 `Access denied`

**解决方案**:
```bash
# 检查MySQL是否运行
# Windows (XAMPP):
# 打开XAMPP控制面板，确保MySQL服务已启动（绿色按钮）

# Windows (命令行):
net start MySQL80

# 检查 .env 文件中的数据库配置
# backend/.env
DATABASE_URL=mysql+aiomysql://root:@localhost:3306/print_erp?charset=utf8mb4
#                                  ↑ 如果MySQL有密码，这里填写密码
```

### 问题3: Alembic迁移失败

**错误信息**: `Target database is not up to date` 或 `Can't locate revision`

**解决方案**:
```bash
cd backend

# 查看当前迁移状态
poetry run alembic current

# 升级到最新版本
poetry run alembic upgrade head

# 如果还是失败，查看迁移历史
poetry run alembic history
```

### 问题4: 初始化数据失败（Duplicate entry）

**错误信息**: `(1062, "Duplicate entry 'PAPER-001' for key 'ix_erp_materials_code'")`

**原因**: 数据已经初始化过，不能重复初始化

**解决方案**:
```bash
# 方案1: 跳过初始化，直接使用现有数据
# 数据已存在，可以直接登录使用

# 方案2: 清空数据库重新初始化
# 登录MySQL，执行：
DROP DATABASE print_erp;
CREATE DATABASE print_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 然后重新迁移和初始化
cd backend
poetry run alembic upgrade head
poetry run python scripts/init_db.py
```

### 问题5: 前端API请求404

**错误信息**: `404 Not Found` 或 `Cannot GET /api/v1/...`

**原因**: 后端服务未启动或API路径错误

**解决方案**:
```bash
# 1. 确认后端已启动
# 访问 http://localhost:8000
# 应该看到: {"message":"Print-ERP API Server",...}

# 2. 检查 frontend/.env 配置
VITE_API_BASE_URL=http://localhost:8000

# 3. 检查API路径
# 所有API路径都以 /api/v1/ 开头
# 例如: http://localhost:8000/api/v1/auth/login
```

### 问题6: 前端依赖安装失败

**错误信息**: `npm ERR! code ERESOLVE` 或网络超时

**解决方案**:
```bash
cd frontend

# 方案1: 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install

# 方案2: 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install

# 方案3: 使用 --legacy-peer-deps
npm install --legacy-peer-deps
```

### 问题7: 后端Poetry依赖安装失败

**错误信息**: `SolverProblemError` 或依赖冲突

**解决方案**:
```bash
cd backend

# 方案1: 更新Poetry
poetry self update

# 方案2: 清除缓存
poetry cache clear . --all
poetry install

# 方案3: 使用国内镜像
poetry source add --priority=default mirrors https://pypi.tuna.tsinghua.edu.cn/simple/
poetry install
```

### 问题8: 用户名或密码错误

**错误信息**: `用户名或密码错误`

**原因**: 数据未正确初始化或密码输入错误

**解决方案**:
```bash
# 1. 确认使用正确的账号
# 用户名: admin
# 密码: admin123

# 2. 检查数据库是否有用户数据
# 登录MySQL执行:
USE print_erp;
SELECT username, role FROM sys_users;

# 3. 如果没有数据，重新初始化
cd backend
poetry run python scripts/init_db.py
```

---

## 🔧 开发工具链接

启动成功后，可以访问以下地址：

| 工具 | 链接 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:5173 (或5174) | Vue 3 SPA |
| 后端API | http://localhost:8000 | FastAPI服务 |
| API文档 | http://localhost:8000/docs | Swagger UI |
| ReDoc文档 | http://localhost:8000/redoc | API参考文档 |
| 数据库 | localhost:3306 | MySQL (XAMPP) |

---

## 📚 下一步学习

### 了解架构

- 📖 [backend/README.md](backend/README.md) - 后端架构详解
- 📖 [frontend/README.md](frontend/README.md) - 前端架构详解
- 📋 [印刷行业 ERP 系统开发规格说明书.md](印刷行业%20ERP%20系统开发规格说明书.md) - 业务逻辑

### 了解设计

- 🎨 [印刷 ERP 前端 UIUX 设计规范.md](印刷%20ERP%20前端%20UIUX%20设计规范.md) - UI/UX设计系统
- 🌈 了解Modern Bento Grid布局
- 💎 学习Linear风格设计

### 开发新功能

- 🔧 完善订单管理前端页面
- 🏭 实现生产工单模块
- 📊 添加数据报表功能
- 📱 适配移动端

---

## 💡 使用技巧

### 1. 快捷键

- **Ctrl + K** - 全局搜索（未实现）
- **Ctrl + /** - 切换侧边栏（未实现）
- **Esc** - 关闭对话框

### 2. 数据查看

使用浏览器开发者工具（F12）：
- **Network** 标签 - 查看API请求
- **Console** 标签 - 查看前端日志
- **Application** → **Local Storage** - 查看Token

### 3. 后端日志

后端控制台会实时显示：
- API请求日志
- SQL查询日志
- 错误堆栈

### 4. 热重载

- **后端**: 修改Python代码后自动重启（约2秒）
- **前端**: 修改Vue代码后自动刷新（即时）

---

## 🆘 获取帮助

如遇问题：

1. **查看控制台** - 前端（F12）和后端控制台的错误信息
2. **检查日志** - 后端日志会显示详细的错误堆栈
3. **测试API** - 访问 http://localhost:8000/docs 直接测试接口
4. **参考文档** - 查看本项目的其他Markdown文档
5. **提交Issue** - 到项目仓库提交问题报告

---

## 🎉 启动成功检查清单

在开始使用前，请确认：

- ✅ MySQL服务正在运行（XAMPP绿色按钮）
- ✅ 后端启动成功（http://localhost:8000 可访问）
- ✅ 前端启动成功（http://localhost:5173 或 5174 可访问）
- ✅ 数据库已创建（print_erp）
- ✅ 数据已初始化（3个用户 + 8个物料）
- ✅ CORS配置正确（前端端口已添加到后端配置）
- ✅ 可以成功登录（admin/admin123）

---

## 📝 版本信息

- **项目版本**: v1.0.0
- **后端框架**: FastAPI (最新)
- **前端框架**: Vue 3.5+
- **数据库**: MySQL 8.0
- **Python**: 3.10+
- **Node.js**: 18+

---

**祝你使用愉快！** 🎉

如果本指南帮助到你，请给项目点个Star ⭐
