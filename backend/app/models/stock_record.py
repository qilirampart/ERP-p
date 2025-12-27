"""
库存流水记录模型
表名: erp_stock_records
功能: 记录所有库存变动历史
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, Numeric, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum


class StockOperationType(str, enum.Enum):
    """库存操作类型枚举"""
    IN = "IN"              # 入库
    OUT = "OUT"            # 出库
    ADJUST = "ADJUST"      # 库存调整
    RETURN = "RETURN"      # 退货入库
    SCRAP = "SCRAP"        # 报废出库


class StockRecord(Base):
    """库存流水记录模型"""
    __tablename__ = "erp_stock_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 关联物料
    material_id: Mapped[int] = mapped_column(
        ForeignKey("erp_materials.id", ondelete="CASCADE"),
        index=True,
        comment="物料ID"
    )

    # 操作信息
    operation_type: Mapped[StockOperationType] = mapped_column(
        SQLEnum(StockOperationType),
        comment="操作类型"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        comment="变动数量（正数=入库，负数=出库）"
    )
    unit: Mapped[str] = mapped_column(
        String(10),
        comment="操作单位（如：令、吨、张）"
    )

    # 库存快照
    before_stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        comment="操作前库存（张）"
    )
    after_stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        comment="操作后库存（张）"
    )

    # 关联信息（可选）
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="关联订单ID"
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="操作人ID"
    )

    # 备注
    remark: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注说明"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        comment="创建时间"
    )

    # 关系
    material: Mapped["Material"] = relationship(
        "Material",
        back_populates="stock_records"
    )
    # operator关系使用字符串引用，避免循环导入
    # 实际使用时可以通过 operator_id 查询

    def __repr__(self) -> str:
        return f"<StockRecord(id={self.id}, material_id={self.material_id}, type={self.operation_type}, qty={self.quantity})>"
