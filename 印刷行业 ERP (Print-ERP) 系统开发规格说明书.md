# 印刷行业 ERP (Print-ERP) 系统开发规格说明书

版本： V1.1 (详细实施版)

适用对象： 后端开发(Python)、前端开发(Vue)、AI 编程助手

------

## 1. 技术栈与环境规范 (Tech Stack)

所有开发工作必须严格遵守以下版本和库的选择，严禁随意引入未经批准的第三方库。

### 1.1 后端 (Backend)

- **语言:** Python 3.10+
- **Web 框架:** FastAPI (最新版)
- **ASGI 服务器:** Uvicorn
- **ORM 框架:** SQLAlchemy 2.0+ (必须使用 **Async** 模式 + `MappedAsDataclass` 风格)
- **数据验证:** Pydantic V2 (严禁使用 V1)
- **数据库迁移:** Alembic
- **依赖管理:** Poetry
- **任务队列:** Celery + Redis (用于耗时计算)
- **工具库:** Pandas (数据处理), Jinja2 (模板渲染)

### 1.2 前端 (Frontend)

- **框架:** Vue 3 (Composition API, `<script setup>`)
- **构建工具:** Vite 5+
- **UI 组件库:** Element Plus (必须按需加载)
- **状态管理:** Pinia
- **HTTP 客户端:** Axios
- **CSS 框架:** Tailwind CSS (用于布局) + SCSS

### 1.3 基础设施 (Infra)

- **数据库:** MySQL 8.0 (字符集 `utf8mb4`)
- **缓存:** Redis 7.0

------

## 2. 后端项目详细结构

开发时必须保持此目录结构，不得扁平化。

Plaintext

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py          # 登录与权限
│   │   │   │   ├── materials.py     # 物料管理
│   │   │   │   ├── orders.py        # 订单管理
│   │   │   │   ├── quotes.py        # 自动报价(独立入口)
│   │   │   │   └── production.py    # 生产报工
│   │   │   └── api.py               # 路由注册中心
│   │   └── deps.py                  # 依赖注入 (DB Session, Current User)
│   ├── core/
│   │   ├── config.py                # Pydantic Settings 配置管理
│   │   └── security.py              # JWT Token 生成与解析
│   ├── db/
│   │   ├── base.py                  # 用于 Alembic 导入所有 Models
│   │   └── session.py               # AsyncEngine 配置
│   ├── models/                      # SQLAlchemy Models (与数据库表一一对应)
│   │   ├── user.py
│   │   ├── material.py
│   │   ├── order.py
│   │   └── production.py
│   ├── schemas/                     # Pydantic Models (Request/Response DTO)
│   │   ├── token.py
│   │   ├── material.py
│   │   └── order.py
│   ├── services/                    # 纯业务逻辑 (解耦 Controller)
│   │   ├── calculation_service.py   # 核心：开纸算法、价格计算
│   │   └── inventory_service.py     # 核心：库存单位换算
│   └── main.py                      # App 入口
├── alembic/                         # 迁移脚本目录
├── tests/                           # Pytest 测试用例
├── poetry.lock
└── pyproject.toml
```

------

## 3. 数据库详细设计 (Schema Specifications)

请 AI 根据以下描述生成 SQLAlchemy Model 代码。所有表必须包含 `created_at` 和 `updated_at` 字段。

### 3.1 用户与权限 (`sys_users`)

- `id`: Int, PK
- `username`: String(50), Unique
- `hashed_password`: String
- `role`: Enum ('ADMIN', 'SALES', 'OPERATOR') - 简单 RBAC

### 3.2 物料表 (`erp_materials`)

核心痛点：库存单位换算。

- `id`: Int, PK
- `code`: String(50), Unique, Index (物料编码)
- `category`: Enum ('PAPER', 'INK', 'AUX')
- `name`: String(100)
- `gram_weight`: Int (克重 g/m²) - *仅纸张有效*
- `spec_length`: Int (mm) - *仅纸张有效*
- `spec_width`: Int (mm) - *仅纸张有效*
- `purchase_unit`: String(10) (采购单位：如 '令', '吨')
- `stock_unit`: String(10) (库存单位：必须为 '张')
- `unit_rate`: Decimal(10,4) (换算率：1令=500张，则为 500)
- `current_stock`: Decimal(12,2) (以 stock_unit 为准)
- `cost_price`: Decimal(10,2) (库存单价)

### 3.3 订单主表 (`erp_orders`)

- `id`: Int, PK
- `order_no`: String(30), Unique (规则: SO+YYYYMMDD+001)
- `customer_name`: String(100)
- `total_amount`: Decimal(12,2)
- `status`: Enum ('DRAFT', 'CONFIRMED', 'PRODUCTION', 'COMPLETED')

### 3.4 订单明细表 (`erp_order_items`)

- `id`: Int, PK
- `order_id`: FK -> erp_orders.id
- `product_name`: String(100)
- `quantity`: Int (印数)
- `finished_size_w`: Int (成品宽)
- `finished_size_h`: Int (成品高)
- `page_count`: Int (P数)
- `paper_material_id`: FK -> erp_materials.id
- `crafts`: JSON (存储工艺详情，如 `{"laminate": "matte", "uv": "spot"}`)

------

## 4. 核心业务逻辑算法 (Implementation Logic)

**这是给 AI 的核心 Prompt 素材，开发时需重点关注。**

### 4.1 核心算法：智能开纸计算 (`calculation_service.py`)

业务背景： 给定大纸尺寸和成品尺寸，计算最大产出数。

逻辑伪代码：

Python

```
def calculate_max_cut(paper_w, paper_h, target_w, target_h):
    # 场景A：直切 (纹路对应)
    cut_a_x = floor(paper_w / target_w)
    cut_a_y = floor(paper_h / target_h)
    total_a = cut_a_x * cut_a_y
    
    # 场景B：横切 (旋转90度)
    cut_b_x = floor(paper_w / target_h)
    cut_b_y = floor(paper_h / target_w)
    total_b = cut_b_x * cut_b_y
    
    # 返回最大值及方案名称
    if total_a >= total_b:
        return {"count": total_a, "method": "DIRECT", "utilization": ...}
    else:
        return {"count": total_b, "method": "ROTATED", "utilization": ...}
```

*要求：后续版本需考虑“修边尺寸”（通常大纸需减去 10mm 咬口位）。*

### 4.2 核心逻辑：库存扣减 (`inventory_service.py`)

业务背景： 订单使用单位是“张”，但有时候采购入库是“令”。

逻辑：

1. 所有库存变动必须在 `services` 层通过事务处理。
2. `current_stock` 永远存储**最小单位（张）**。
3. 入库 API 接收参数：`quantity` (数量), `unit` (单位)。
4. 如果是“令”，则 `stock_change = quantity * material.unit_rate`。
5. 如果是“张”，则 `stock_change = quantity`。

------

## 5. API 接口规范 (API Contract)

### 5.1 响应包装 (Response Wrapper)

所有接口（除 OAuth Token 外）必须返回以下 JSON 结构：

JSON

```
{
  "code": 200,
  "msg": "success",
  "data": { ... }
}
```

### 5.2 关键接口定义

- `POST /api/v1/quotes/calculate`
  - **描述:** 计算报价与开纸方案
  - **入参:** `{ "paper_id": 1, "target_w": 210, "target_h": 285, "quantity": 5000 }`
  - **出参:** `{ "total_price": 1500.00, "cut_method": "DIRECT", "paper_usage": 2500 }`
- `POST /api/v1/materials/`
  - **描述:** 新增物料
  - **入参:** Pydantic Schema `MaterialCreate`
- `GET /api/v1/orders/{id}/production-card`
  - **描述:** 获取生产施工单详情（用于前端打印）

------

## 6. 前端开发指引

### 6.1 组件封装要求

为了应对复杂的印刷表单，必须封装以下业务组件：

- `@/components/business/MaterialSelect.vue`: 带搜索功能的物料选择器，选中后自动填充克重、尺寸。
- `@/components/business/SizeInput.vue`: 双输入框（长 x 宽），带单位显示。

### 6.2 状态管理 (Pinia)

- `useUserStore`: 存储 Token 和用户角色。
- `useConfigStore`: 存储系统字典（如工艺列表、纹路方向枚举），APP 启动时一次性拉取。

------

## 7. AI 辅助开发 Prompt 示例

**当你把任务派发给 AI 时，请使用以下模板：**

> 任务： 编写物料管理的 CRUD 接口。
>
> 上下文： 基于 FastAPI + SQLAlchemy Async。
>
> 输入： > 1. 模型定义：见 models/material.py (你需提供代码)。
>
> 2. Schema 定义：见 schemas/material.py (你需提供代码)。
>
> 要求：
>
> 1. 在 `services/material_service.py` 中编写业务逻辑，包含“检查编码是否重复”。
> 2. 在 `api/v1/endpoints/materials.py` 中编写路由。
> 3. 使用 `deps.get_db` 获取数据库会话。
> 4. 所有函数必须包含 Python 类型提示 (Type Hints)。

------

## 8. 部署与运维

- **Docker:** 必须提供 `Dockerfile` 和 `docker-compose.yml`。
- **环境变量:** 所有敏感信息（DB密码、Secret Key）必须通过 `.env` 文件读取，禁止硬编码。
- **API 文档:** 开发完成后，通过 `/docs` (Swagger UI) 验收接口。

------

**文档结束**