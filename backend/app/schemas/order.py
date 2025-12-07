"""
订单相关Schema
"""
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.order import OrderStatus


class OrderItemBase(BaseModel):
    """订单明细基础Schema"""
    product_name: str = Field(..., max_length=100, description="产品名称")
    quantity: int = Field(..., gt=0, description="印数")
    finished_size_w: int = Field(..., gt=0, description="成品宽度 mm")
    finished_size_h: int = Field(..., gt=0, description="成品高度 mm")
    page_count: int = Field(default=1, gt=0, description="页数")
    paper_material_id: int = Field(..., gt=0, description="纸张物料ID")
    crafts: Optional[dict] = Field(None, description="工艺详情JSON")


class OrderItemCreate(OrderItemBase):
    """创建订单明细Schema"""
    pass


class OrderItemResponse(OrderItemBase):
    """订单明细响应Schema"""
    id: int
    order_id: int
    paper_usage: Optional[int]
    cut_method: Optional[str]
    item_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """订单基础Schema"""
    customer_name: str = Field(..., max_length=100, description="客户名称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    remark: Optional[str] = Field(None, description="备注")


class OrderCreate(OrderBase):
    """创建订单Schema"""
    items: List[OrderItemCreate] = Field(..., min_length=1, description="订单明细列表")


class OrderUpdate(BaseModel):
    """更新订单Schema"""
    customer_name: Optional[str] = Field(None, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=50)
    contact_phone: Optional[str] = Field(None, max_length=20)
    status: Optional[OrderStatus] = None
    remark: Optional[str] = None


class OrderResponse(OrderBase):
    """订单响应Schema"""
    id: int
    order_no: str
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应Schema"""
    id: int
    order_no: str
    customer_name: str
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    items_count: int = 0

    class Config:
        from_attributes = True
