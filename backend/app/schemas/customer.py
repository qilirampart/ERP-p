"""
客户相关Schema
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CustomerBase(BaseModel):
    """客户基础Schema"""
    customer_name: str = Field(..., max_length=100, description="客户名称")
    short_name: Optional[str] = Field(None, max_length=50, description="简称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[EmailStr] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    customer_level: str = Field("C", pattern="^[A-D]$", description="客户等级 A/B/C/D")
    credit_limit: Decimal = Field(Decimal("0.00"), ge=0, description="信用额度")
    tax_number: Optional[str] = Field(None, max_length=50, description="税号")
    remark: Optional[str] = Field(None, description="备注")


class CustomerCreate(CustomerBase):
    """创建客户Schema"""
    pass


class CustomerUpdate(BaseModel):
    """更新客户Schema"""
    customer_name: Optional[str] = Field(None, max_length=100, description="客户名称")
    short_name: Optional[str] = Field(None, max_length=50, description="简称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[EmailStr] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    customer_level: Optional[str] = Field(None, pattern="^[A-D]$", description="客户等级")
    credit_limit: Optional[Decimal] = Field(None, ge=0, description="信用额度")
    tax_number: Optional[str] = Field(None, max_length=50, description="税号")
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE)$", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class CustomerResponse(CustomerBase):
    """客户响应Schema"""
    id: int
    customer_code: str
    status: str
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerListItem(BaseModel):
    """客户列表项Schema"""
    id: int
    customer_code: str
    customer_name: str
    short_name: Optional[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
    customer_level: str
    status: str
    balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerStatistics(BaseModel):
    """客户统计Schema"""
    total_orders: int = Field(description="总订单数")
    total_amount: Decimal = Field(description="总交易额")
    completed_orders: int = Field(description="已完成订单数")
    average_order_amount: Decimal = Field(description="平均订单金额")
    last_order_date: Optional[datetime] = Field(None, description="最近订单日期")
