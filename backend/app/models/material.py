"""
物料模型 - 纸张/油墨/辅料管理
表名: erp_materials
核心功能: 库存单位换算 (unit_rate)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
import enum


class MaterialCategory(str, enum.Enum):
    """物料分类枚举"""
    PAPER = "PAPER"  # 纸张
    INK = "INK"      # 油墨
    AUX = "AUX"      # 辅料


class Material(Base):
    """物料模型"""
    __tablename__ = "erp_materials"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="物料编码")
    category: Mapped[MaterialCategory] = mapped_column(
        SQLEnum(MaterialCategory),
        comment="物料分类"
    )
    name: Mapped[str] = mapped_column(String(100), comment="物料名称")

    # 纸张专用字段（其他类型可为NULL）
    gram_weight: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="克重 g/m²")
    spec_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="纸张长度 mm")
    spec_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="纸张宽度 mm")

    # 单位换算（核心字段）
    purchase_unit: Mapped[str] = mapped_column(String(10), comment="采购单位（如：令、吨）")
    stock_unit: Mapped[str] = mapped_column(String(10), default="张", comment="库存单位（统一为'张'）")
    unit_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        comment="换算率（如：1令=500张，则为500.0000）"
    )

    # 库存与价格
    current_stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        comment="当前库存（以stock_unit为准）"
    )
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        comment="成本单价（元/张）"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<Material(code='{self.code}', name='{self.name}', stock={self.current_stock})>"
