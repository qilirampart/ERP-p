"""
数据库异步会话配置
使用 SQLAlchemy 2.0 Async Engine
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 开发环境打印SQL
    pool_pre_ping=True,   # 连接池预检查
    pool_size=10,
    max_overflow=20
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# 声明式基类（用于所有Model继承）
class Base(DeclarativeBase):
    """SQLAlchemy声明式基类"""
    pass


async def get_db() -> AsyncSession:
    """
    依赖注入：获取数据库会话

    使用示例:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
