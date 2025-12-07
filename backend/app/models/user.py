"""
用户模型 - 系统用户与权限管理
表名: sys_users
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "ADMIN"       # 管理员
    SALES = "SALES"       # 销售人员
    OPERATOR = "OPERATOR" # 操作员（生产/仓库）


class User(Base):
    """用户模型"""
    __tablename__ = "sys_users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    hashed_password: Mapped[str] = mapped_column(String(255), comment="密码哈希")
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.OPERATOR,
        comment="用户角色"
    )
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否激活")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role={self.role})>"
