"""
订单模型 - 订单主表与明细表
表名: erp_orders, erp_order_items
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Integer, Numeric, Enum as SQLEnum, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum


class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    DRAFT = "DRAFT"             # 草稿
    CONFIRMED = "CONFIRMED"     # 已确认
    PRODUCTION = "PRODUCTION"   # 生产中
    COMPLETED = "COMPLETED"     # 已完成


class Order(Base):
    """订单主表"""
    __tablename__ = "erp_orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
        comment="订单编号（格式：SO+YYYYMMDD+001）"
    )
    customer_name: Mapped[str] = mapped_column(String(100), comment="客户名称")
    contact_person: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="联系人")
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="联系电话")

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        comment="订单总金额"
    )
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus),
        default=OrderStatus.DRAFT,
        comment="订单状态"
    )

    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="备注")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    # 关联订单明细（一对多）
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order(order_no='{self.order_no}', customer='{self.customer_name}', status={self.status})>"


class OrderItem(Base):
    """订单明细表"""
    __tablename__ = "erp_order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("erp_orders.id"), comment="订单ID")

    # 产品信息
    product_name: Mapped[str] = mapped_column(String(100), comment="产品名称")
    quantity: Mapped[int] = mapped_column(Integer, comment="印数（成品数量）")

    # 成品尺寸
    finished_size_w: Mapped[int] = mapped_column(Integer, comment="成品宽度 mm")
    finished_size_h: Mapped[int] = mapped_column(Integer, comment="成品高度 mm")
    page_count: Mapped[int] = mapped_column(Integer, default=1, comment="页数（P数）")

    # 纸张选择
    paper_material_id: Mapped[int] = mapped_column(
        ForeignKey("erp_materials.id"),
        comment="纸张物料ID"
    )

    # 工艺信息（JSON存储）
    # 示例: {"laminate": "matte", "uv": "spot", "binding": "saddle_stitch"}
    crafts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="工艺详情JSON")

    # 计算结果（由开纸算法填充）
    paper_usage: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="纸张消耗数（张）"
    )
    cut_method: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="开纸方案（DIRECT/ROTATED）"
    )

    # 明细金额
    item_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        comment="明细金额"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    # 反向关联订单主表
    order: Mapped["Order"] = relationship("Order", back_populates="items")

    # 关联纸张物料
    paper_material: Mapped["Material"] = relationship("Material")

    def __repr__(self) -> str:
        return f"<OrderItem(product='{self.product_name}', qty={self.quantity})>"
