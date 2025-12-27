"""
库存流水记录相关Schema
"""
from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.stock_record import StockOperationType


class StockRecordBase(BaseModel):
    """库存流水基础Schema"""
    material_id: int = Field(..., description="物料ID")
    operation_type: StockOperationType = Field(..., description="操作类型")
    quantity: Decimal = Field(..., description="变动数量")
    unit: str = Field(..., max_length=10, description="操作单位")
    before_stock: Decimal = Field(..., description="操作前库存")
    after_stock: Decimal = Field(..., description="操作后库存")
    order_id: Optional[int] = Field(None, description="关联订单ID")
    operator_id: Optional[int] = Field(None, description="操作人ID")
    remark: Optional[str] = Field(None, description="备注说明")


class StockRecordCreate(BaseModel):
    """创建库存流水Schema（内部使用）"""
    material_id: int
    operation_type: StockOperationType
    quantity: Decimal
    unit: str
    before_stock: Decimal
    after_stock: Decimal
    order_id: Optional[int] = None
    operator_id: Optional[int] = None
    remark: Optional[str] = None


class StockRecordResponse(StockRecordBase):
    """库存流水响应Schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StockRecordWithMaterial(StockRecordResponse):
    """带物料信息的库存流水响应Schema"""
    material_code: str = Field(description="物料编码")
    material_name: str = Field(description="物料名称")
    operator_name: Optional[str] = Field(None, description="操作人姓名")

    class Config:
        from_attributes = True
