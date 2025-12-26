"""
客户模型
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class CustomerLevel(str, enum.Enum):
    """客户等级"""
    A = "A"  # 重要客户
    B = "B"  # 优质客户
    C = "C"  # 普通客户
    D = "D"  # 潜在客户


class CustomerStatus(str, enum.Enum):
    """客户状态"""
    ACTIVE = "ACTIVE"      # 活跃
    INACTIVE = "INACTIVE"  # 停用


class Customer(Base):
    """客户表"""
    __tablename__ = "erp_customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(30), unique=True, nullable=False, comment="客户编码")
    customer_name = Column(String(100), nullable=False, index=True, comment="客户名称")
    short_name = Column(String(50), comment="简称")
    contact_person = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), index=True, comment="联系电话")
    contact_email = Column(String(100), comment="邮箱")
    address = Column(Text, comment="地址")
    customer_level = Column(
        SQLEnum(CustomerLevel),
        nullable=False,
        default=CustomerLevel.C,
        comment="客户等级"
    )
    credit_limit = Column(DECIMAL(12, 2), nullable=False, default=0, comment="信用额度")
    balance = Column(DECIMAL(12, 2), nullable=False, default=0, comment="账户余额")
    tax_number = Column(String(50), comment="税号")
    status = Column(
        SQLEnum(CustomerStatus),
        nullable=False,
        default=CustomerStatus.ACTIVE,
        index=True,
        comment="状态"
    )
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 关系
    orders = relationship("Order", back_populates="customer")
