"""
生产工单数据模型
"""
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum, DECIMAL, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import enum

from app.db.session import Base


class ProductionStatus(str, enum.Enum):
    """生产工单状态"""
    PENDING = "PENDING"  # 待生产
    IN_PROGRESS = "IN_PROGRESS"  # 生产中
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消


class ProductionOrder(Base):
    """生产工单表"""
    __tablename__ = "erp_production_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 工单信息
    production_no: Mapped[str] = mapped_column(String(30), unique=True, index=True, comment="生产工单号 PO+YYYYMMDD+序号")
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("erp_orders.id"), comment="关联订单ID")

    # 生产计划
    plan_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="计划开始时间")
    plan_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="计划完成时间")

    # 生产实际
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="实际开始时间")
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="实际完成时间")

    # 生产信息
    status: Mapped[str] = mapped_column(
        SQLEnum(ProductionStatus),
        default=ProductionStatus.PENDING,
        comment="生产状态"
    )
    priority: Mapped[int] = mapped_column(Integer, default=5, comment="优先级 1-10，数字越小优先级越高")

    # 生产人员
    operator_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="操作员姓名")
    machine_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="设备名称")

    # 备注
    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="备注")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )

    # 关联关系
    order: Mapped["Order"] = relationship("Order", back_populates="production_orders")
    items: Mapped[list["ProductionOrderItem"]] = relationship(
        "ProductionOrderItem",
        back_populates="production_order",
        cascade="all, delete-orphan"
    )
    reports: Mapped[list["ProductionReport"]] = relationship(
        "ProductionReport",
        back_populates="production_order",
        cascade="all, delete-orphan"
    )


class ProductionOrderItem(Base):
    """生产工单明细表"""
    __tablename__ = "erp_production_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联
    production_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("erp_production_orders.id"), comment="生产工单ID")
    order_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("erp_order_items.id"), comment="订单明细ID")

    # 生产信息
    product_name: Mapped[str] = mapped_column(String(100), comment="产品名称")
    plan_quantity: Mapped[int] = mapped_column(Integer, comment="计划生产数量")
    completed_quantity: Mapped[int] = mapped_column(Integer, default=0, comment="已完成数量")
    rejected_quantity: Mapped[int] = mapped_column(Integer, default=0, comment="报废数量")

    # 工艺信息（从订单明细复制）
    finished_size_w: Mapped[int] = mapped_column(Integer, comment="成品宽度mm")
    finished_size_h: Mapped[int] = mapped_column(Integer, comment="成品高度mm")
    page_count: Mapped[int] = mapped_column(Integer, comment="页数P数")
    paper_material_id: Mapped[int] = mapped_column(Integer, ForeignKey("erp_materials.id"), comment="纸张物料ID")

    # 开纸方案（从订单明细复制）
    paper_usage: Mapped[int] = mapped_column(Integer, comment="纸张消耗数量")
    cut_method: Mapped[str] = mapped_column(String(20), comment="开纸方案 DIRECT/ROTATED")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    # 关联关系
    production_order: Mapped["ProductionOrder"] = relationship("ProductionOrder", back_populates="items")
    order_item: Mapped["OrderItem"] = relationship("OrderItem")
    paper_material: Mapped["Material"] = relationship("Material")


class ProductionReport(Base):
    """生产报工记录表"""
    __tablename__ = "erp_production_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联
    production_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("erp_production_orders.id"), comment="生产工单ID")

    # 报工信息
    report_type: Mapped[str] = mapped_column(
        String(20),
        comment="报工类型: START(开工)/PROGRESS(进度)/COMPLETE(完工)/REJECT(报废)"
    )
    completed_quantity: Mapped[int] = mapped_column(Integer, default=0, comment="本次完成数量")
    rejected_quantity: Mapped[int] = mapped_column(Integer, default=0, comment="本次报废数量")

    # 报工人员
    operator_name: Mapped[str] = mapped_column(String(50), comment="操作员姓名")
    operator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sys_users.id"), nullable=True, comment="操作员用户ID")

    # 报工说明
    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="报工说明")

    # 时间戳
    report_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="报工时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    # 关联关系
    production_order: Mapped["ProductionOrder"] = relationship("ProductionOrder", back_populates="reports")
    operator: Mapped[Optional["User"]] = relationship("User")
