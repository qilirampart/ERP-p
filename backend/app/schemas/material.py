"""
物料相关Schema
"""
from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.material import MaterialCategory


class MaterialBase(BaseModel):
    """物料基础Schema"""
    code: str = Field(..., max_length=50, description="物料编码")
    category: MaterialCategory = Field(..., description="物料分类")
    name: str = Field(..., max_length=100, description="物料名称")
    gram_weight: Optional[int] = Field(None, description="克重 g/m²（仅纸张）")
    spec_length: Optional[int] = Field(None, description="纸张长度 mm")
    spec_width: Optional[int] = Field(None, description="纸张宽度 mm")
    purchase_unit: str = Field(..., max_length=10, description="采购单位")
    unit_rate: Decimal = Field(..., gt=0, description="换算率")
    cost_price: Decimal = Field(default=Decimal("0.00"), ge=0, description="成本单价")
    min_stock: Decimal = Field(default=Decimal("0.00"), ge=0, description="最低库存预警值")
    safety_stock: Decimal = Field(default=Decimal("0.00"), ge=0, description="安全库存值")


class MaterialCreate(MaterialBase):
    """创建物料Schema"""
    pass


class MaterialUpdate(BaseModel):
    """更新物料Schema（所有字段可选）"""
    name: Optional[str] = Field(None, max_length=100)
    gram_weight: Optional[int] = None
    spec_length: Optional[int] = None
    spec_width: Optional[int] = None
    cost_price: Optional[Decimal] = Field(None, ge=0)
    current_stock: Optional[Decimal] = Field(None, ge=0)
    min_stock: Optional[Decimal] = Field(None, ge=0)
    safety_stock: Optional[Decimal] = Field(None, ge=0)


class MaterialResponse(MaterialBase):
    """物料响应Schema"""
    id: int
    stock_unit: str
    current_stock: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaterialWithStatus(MaterialResponse):
    """带库存状态的物料响应Schema"""
    stock_status: str = Field(description="库存状态: NORMAL/WARNING/CRITICAL")

    class Config:
        from_attributes = True


class StockOperationRequest(BaseModel):
    """库存操作请求"""
    material_id: int = Field(..., gt=0, description="物料ID")
    quantity: Decimal = Field(..., gt=0, description="数量")
    unit: str = Field(..., max_length=10, description="单位")
