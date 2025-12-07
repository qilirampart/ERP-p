# Print-ERP 后端

印刷行业ERP系统后端服务 - 基于 FastAPI + SQLAlchemy Async

## 技术栈

- **Python 3.10+**
- **FastAPI** - Web框架
- **SQLAlchemy 2.0** - ORM (Async模式)
- **Pydantic V2** - 数据验证
- **MySQL 8.0** - 数据库
- **Alembic** - 数据库迁移
- **Poetry** - 依赖管理

## 快速开始

### 1. 安装依赖

```bash
# 安装Poetry（如果未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
cd backend
poetry install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，配置数据库连接
# DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/print_erp?charset=utf8mb4
```

### 3. 初始化数据库

```bash
# 创建数据库（在MySQL中执行）
CREATE DATABASE print_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 生成初始迁移
poetry run alembic revision --autogenerate -m "Initial migration"

# 执行迁移
poetry run alembic upgrade head
```

### 4. 创建初始管理员用户

```bash
# 进入Poetry Shell
poetry shell

# 运行Python交互式环境
python

# 执行以下代码
```

```python
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as session:
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print("管理员账号创建成功: admin / admin123")

asyncio.run(create_admin())
```

### 5. 启动开发服务器

```bash
# 方式1：使用uvicorn直接运行
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式2：使用Python运行
poetry run python -m app.main
```

服务将在 http://localhost:8000 启动

## API文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 核心功能模块

### 1. 认证模块 (`/api/v1/auth`)
- `POST /login` - 用户登录
- `POST /token` - OAuth2 Token获取

### 2. 物料管理 (`/api/v1/materials`)
- `POST /` - 创建物料
- `GET /` - 获取物料列表
- `GET /{id}` - 获取物料详情
- `PUT /{id}` - 更新物料
- `POST /stock-in` - 入库操作
- `POST /stock-out` - 出库操作

### 3. 报价计算 (`/api/v1/quotes`)
- `POST /calculate` - 智能开纸计算与自动报价

## 核心算法

### 智能开纸计算 (`calculation_service.py`)

给定大纸尺寸和成品尺寸，自动计算最优切割方案：
- 直切方案（纹路对应）
- 横切方案（旋转90°）
- 自动选择利用率最高的方案

### 库存单位换算 (`inventory_service.py`)

支持不同单位间的自动换算：
- 采购单位（令/吨）→ 库存单位（张）
- 库存单位（张）→ 显示单位（任意）

## 项目结构

```
backend/
├── app/
│   ├── api/v1/endpoints/    # API端点
│   ├── core/                # 核心配置
│   ├── db/                  # 数据库配置
│   ├── models/              # SQLAlchemy模型
│   ├── schemas/             # Pydantic Schemas
│   ├── services/            # 业务逻辑层
│   └── main.py              # 应用入口
├── alembic/                 # 数据库迁移
├── tests/                   # 测试用例
├── pyproject.toml           # Poetry配置
└── .env                     # 环境变量
```

## 开发规范

1. **异步优先**: 所有数据库操作使用 `async/await`
2. **类型提示**: 所有函数必须包含完整的类型提示
3. **响应包装**: 所有API返回统一格式 `{code, msg, data}`
4. **业务分层**: 复杂逻辑放在 `services/` 层

## 常用命令

```bash
# 创建新的数据库迁移
poetry run alembic revision --autogenerate -m "描述"

# 执行迁移
poetry run alembic upgrade head

# 回滚迁移
poetry run alembic downgrade -1

# 代码格式化
poetry run black app/

# 类型检查
poetry run mypy app/

# 运行测试
poetry run pytest
```

## 生产部署

```bash
# 使用Gunicorn + Uvicorn Worker
poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## License

MIT
