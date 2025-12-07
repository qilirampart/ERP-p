# Print-ERP 快速启动指南

本指南将帮助你在 **5分钟内** 启动整个系统。

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

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE print_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 第2步: 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖（首次运行）
poetry install

# 配置环境变量
cp .env.example .env

# 编辑 .env 文件，修改数据库连接
# DATABASE_URL=mysql+aiomysql://root:你的密码@localhost:3306/print_erp?charset=utf8mb4

# 执行数据库迁移
poetry run alembic upgrade head

# 初始化数据（创建账号和示例数据）
poetry run python scripts/init_db.py

# 启动后端服务
poetry run uvicorn app.main:app --reload --port 8000
```

✅ 后端启动成功！访问 http://localhost:8000/docs 查看API文档

### 第3步: 启动前端

**打开新终端**，执行：

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

✅ 前端启动成功！访问 http://localhost:5173

---

## 🎯 登录测试

打开浏览器访问 **http://localhost:5173**

使用以下账号登录：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 销售 | sales | sales123 |
| 操作员 | operator | operator123 |

---

## ✅ 功能测试清单

### 1. 测试物料管理 🏷️

1. 点击左侧 **库存管理**
2. 查看系统已初始化的 8 个物料（5种纸张、2种油墨、2种辅料）
3. 点击 **入库** 按钮，测试入库功能
   - 物料: 双铜纸 157g
   - 数量: 2
   - 单位: 令
   - 提交后，库存应增加 1000张（2令 × 500张/令）

### 2. 测试智能报价 💰

1. 点击左侧 **销售开单**（或直接访问仪表盘的快速操作）
2. 填写产品规格：
   - 选择纸张: 双铜纸 157g - 787×1092mm
   - 成品尺寸: 210 × 285 mm (A4)
   - 印数: 1000
   - 页数: 4
3. 选择工艺：覆哑膜、骑马钉
4. 点击 **智能计算报价**
5. 查看右侧报价结果：
   - ✅ 开纸方案（直切/横切）
   - ✅ 纸张利用率
   - ✅ 纸张消耗
   - ✅ 费用明细（纸张成本、印刷工费、工艺费用）
   - ✅ 总金额

**预期结果**：
- 开数: 16开
- 利用率: 约 95%
- 纸张消耗: 约 125 张

### 3. 测试API接口 📡

访问 http://localhost:8000/docs

尝试以下接口：
1. **POST /api/v1/auth/login** - 登录获取Token
2. **GET /api/v1/materials/** - 获取物料列表
3. **POST /api/v1/quotes/calculate** - 计算报价

---

## 🎨 UI/UX 特色体验

本系统采用 **Modern Bento Grid** 设计：

- 🎯 **大圆角卡片** - 24px圆角，现代感十足
- 💎 **Indigo配色** - #4F46E5 主色，Linear风格
- ✨ **悬浮动效** - 卡片hover时轻微上浮
- 🌈 **通透质感** - 磨砂玻璃效果
- 📊 **数字等宽** - Inter字体，金额显示清晰

---

## 🐛 常见问题

### 问题1: 数据库连接失败

**错误**: `Can't connect to MySQL server`

**解决**:
```bash
# 检查MySQL是否运行
# Windows:
net start MySQL80

# 检查.env文件中的数据库配置
# 确保用户名、密码、端口正确
```

### 问题2: Alembic迁移失败

**错误**: `Target database is not up to date`

**解决**:
```bash
cd backend
poetry run alembic upgrade head
```

### 问题3: 前端API请求失败

**错误**: `Network Error` 或 `CORS Error`

**解决**:
- 确保后端已启动 (http://localhost:8000)
- 检查 `frontend/.env` 中的 `VITE_API_BASE_URL`
- 清除浏览器缓存并刷新

### 问题4: 初始化数据失败

**解决**:
```bash
cd backend
# 先删除旧数据（如果需要）
# 重新执行初始化
poetry run python scripts/init_db.py
```

---

## 📚 下一步学习

- 📖 阅读 `backend/README.md` 了解后端架构
- 📖 阅读 `frontend/README.md` 了解前端架构
- 🎨 查看 `印刷 ERP 前端 UIUX 设计规范.md` 了解设计系统
- 📋 查看 `印刷行业 ERP 系统开发规格说明书.md` 了解业务逻辑

---

## 🆘 获取帮助

如遇问题：
1. 查看控制台错误信息
2. 检查后端日志
3. 访问 http://localhost:8000/docs 测试API
4. 提交 Issue 到项目仓库

---

**祝你使用愉快！** 🎉
