# Print-ERP - 印刷行业ERP系统

现代化的印刷行业企业资源规划系统，专注于智能开纸计算、自动报价和生产管理。

## 项目特色

### 🎯 核心功能
- **智能开纸计算** - 自动计算最优切割方案（直切/横切），最大化纸张利用率
- **自动报价系统** - 基于材料成本、印刷工费、工艺费用的智能报价
- **库存单位换算** - 支持令/吨/张等多单位自动换算
- **生产施工单** - 完整的生产流程管理

### 💎 技术亮点
- **现代化UI/UX** - Linear风格 + Bento Grid布局
- **全栈异步** - 后端AsyncIO + 前端Async/Await
- **类型安全** - Pydantic V2 + TypeScript-ready
- **容器化部署** - Docker + Docker Compose

## 技术栈

### 后端
- **Python 3.10+**
- **FastAPI** - 高性能Web框架
- **SQLAlchemy 2.0** - Async ORM
- **Pydantic V2** - 数据验证
- **MySQL 8.0** - 数据库
- **Redis** - 缓存
- **Alembic** - 数据库迁移

### 前端
- **Vue 3** - Composition API
- **Vite 5** - 构建工具
- **Element Plus** - UI组件库
- **Tailwind CSS** - 样式框架
- **Pinia** - 状态管理

## 项目结构

```
ERP-p/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API端点
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic Schemas
│   │   ├── services/       # 业务逻辑
│   │   │   ├── calculation_service.py  # 开纸算法
│   │   │   └── inventory_service.py    # 库存管理
│   │   └── main.py
│   └── README.md
├── frontend/                # 前端应用
│   ├── src/
│   │   ├── api/            # API封装
│   │   ├── components/     # 组件
│   │   ├── router/         # 路由
│   │   ├── stores/         # 状态管理
│   │   ├── styles/         # 样式
│   │   └── views/          # 页面
│   └── README.md
└── README.md               # 本文件
```

## 快速开始

### 前置要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0
- Redis 7.0

### 1. 克隆项目

```bash
git clone <repository-url>
cd ERP-p
```

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库连接

# 创建数据库
mysql -u root -p
CREATE DATABASE print_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 执行数据库迁移
poetry run alembic upgrade head

# 创建管理员账户（见 backend/README.md）

# 启动后端服务
poetry run uvicorn app.main:app --reload --port 8000
```

后端将在 http://localhost:8000 启动

### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

### 4. 访问应用

打开浏览器访问 http://localhost:5173

默认管理员账号:
- 用户名: `admin`
- 密码: `admin123`

## 核心算法说明

### 智能开纸计算

给定大纸尺寸 (W×H) 和成品尺寸 (w×h)，计算两种切割方案：

**方案A (直切):**
```
开数 = floor(W/w) × floor(H/h)
```

**方案B (横切/旋转90°):**
```
开数 = floor(W/h) × floor(H/w)
```

系统自动选择开数更大的方案，并计算纸张利用率。

### 库存单位换算

所有库存统一以"张"为单位存储，支持：
- 采购单位（令/吨） → 库存单位（张）
- 库存单位（张） → 显示单位（任意）

换算公式：
```
库存数量(张) = 采购数量 × unit_rate
```

例如：入库 2令，unit_rate=500，则库存增加 1000张

## API文档

启动后端后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

主要接口：
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/quotes/calculate` - 智能报价计算
- `GET /api/v1/materials/` - 获取物料列表
- `POST /api/v1/materials/stock-in` - 物料入库

## 开发规范

### 后端
- 所有数据库操作使用 `async/await`
- 所有函数包含完整类型提示
- API响应统一格式: `{code, msg, data}`
- 业务逻辑放在 `services/` 层

### 前端
- 使用 Composition API + `<script setup>`
- 所有页面使用 Bento Card 包裹
- 遵循 Modern Bento 设计规范
- API调用通过 `@/api/` 模块

## 部署

### Docker部署（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产部署

详见：
- 后端部署: `backend/README.md`
- 前端部署: `frontend/README.md`

## 开发进度

### ✅ 已完成
- [x] 后端项目初始化
- [x] 数据库模型设计
- [x] 核心业务算法（开纸计算、库存换算）
- [x] 基础API接口（认证、物料、报价）
- [x] 前端项目初始化
- [x] UI设计系统
- [x] 基础页面（登录、仪表盘、布局）

### 🚧 开发中
- [ ] 订单管理完整功能
- [ ] 生产工单流程
- [ ] 数据报表
- [ ] 权限管理

### 📅 计划中
- [ ] 移动端适配
- [ ] 数据导入/导出
- [ ] 微信通知
- [ ] 客户端打印

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。

---

**PrintOS** - 让印刷管理更简单 🎨
