"""
收款管理Schema
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class PaymentMethodEnum:
    """收款方式"""
    CASH = "CASH"                   # 现金
    BANK_TRANSFER = "BANK_TRANSFER" # 银行转账
    ALIPAY = "ALIPAY"              # 支付宝
    WECHAT = "WECHAT"              # 微信
    CHECK = "CHECK"                # 支票
    OTHER = "OTHER"                # 其他


class PaymentStatusEnum:
    """收款状态"""
    PENDING = "PENDING"       # 待确认
    CONFIRMED = "CONFIRMED"   # 已确认
    CANCELLED = "CANCELLED"   # 已取消


class OrderPaymentCreate(BaseModel):
    """创建收款记录"""
    order_id: int = Field(..., description="订单ID")
    payment_amount: Decimal = Field(..., gt=0, description="收款金额")
    payment_method: str = Field(..., description="收款方式")
    payment_date: datetime = Field(..., description="收款日期")
    received_by: str = Field(..., min_length=1, max_length=50, description="收款人")
    voucher_no: Optional[str] = Field(None, max_length=50, description="凭证号")
    remark: Optional[str] = Field(None, description="备注")

    model_config = ConfigDict(from_attributes=True)


class OrderPaymentUpdate(BaseModel):
    """更新收款记录"""
    payment_amount: Optional[Decimal] = Field(None, gt=0, description="收款金额")
    payment_method: Optional[str] = Field(None, description="收款方式")
    payment_date: Optional[datetime] = Field(None, description="收款日期")
    received_by: Optional[str] = Field(None, min_length=1, max_length=50, description="收款人")
    voucher_no: Optional[str] = Field(None, max_length=50, description="凭证号")
    remark: Optional[str] = Field(None, description="备注")

    model_config = ConfigDict(from_attributes=True)


class OrderPaymentResponse(BaseModel):
    """收款记录响应"""
    id: int
    order_id: int
    payment_no: str
    payment_amount: Decimal
    payment_method: str
    payment_date: datetime
    status: str
    received_by: str
    voucher_no: Optional[str]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    # 关联信息
    order_no: Optional[str] = None
    customer_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderPaymentSummary(BaseModel):
    """订单收款汇总"""
    order_id: int
    order_no: str
    customer_name: str
    total_amount: Decimal           # 订单总金额
    paid_amount: Decimal            # 已收款金额
    unpaid_amount: Decimal          # 未收款金额
    payment_count: int              # 收款次数
    payment_status: str             # 收款状态：UNPAID/PARTIAL/PAID

    model_config = ConfigDict(from_attributes=True)
