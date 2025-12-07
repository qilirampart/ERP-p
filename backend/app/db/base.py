"""
导入所有模型，供Alembic使用
在执行迁移时，Alembic需要导入这个文件来发现所有模型
"""
from app.db.session import Base

# 导入所有模型（必须在这里导入，Alembic才能识别）
from app.models.user import User
from app.models.material import Material
from app.models.order import Order, OrderItem

__all__ = ["Base", "User", "Material", "Order", "OrderItem"]
