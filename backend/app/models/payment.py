"""
收款管理模型
表名: erp_order_payments
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, Numeric, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum


class PaymentMethod(str, enum.Enum):
    """收款方式枚举"""
    CASH = "CASH"                   # 现金
    BANK_TRANSFER = "BANK_TRANSFER" # 银行转账
    ALIPAY = "ALIPAY"              # 支付宝
    WECHAT = "WECHAT"              # 微信
    CHECK = "CHECK"                # 支票
    OTHER = "OTHER"                # 其他


class PaymentStatus(str, enum.Enum):
    """收款状态枚举"""
    PENDING = "PENDING"       # 待确认
    CONFIRMED = "CONFIRMED"   # 已确认
    CANCELLED = "CANCELLED"   # 已取消


class OrderPayment(Base):
    """订单收款记录表"""
    __tablename__ = "erp_order_payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 关联订单
    order_id: Mapped[int] = mapped_column(
        ForeignKey("erp_orders.id"),
        index=True,
        comment="订单ID"
    )

    # 收款信息
    payment_no: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
        comment="收款单号（格式：PAY+YYYYMMDD+001）"
    )
    payment_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        comment="收款金额"
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod),
        comment="收款方式"
    )
    payment_date: Mapped[datetime] = mapped_column(
        comment="收款日期"
    )

    # 状态
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        comment="收款状态"
    )

    # 收款人信息
    received_by: Mapped[str] = mapped_column(
        String(50),
        comment="收款人"
    )

    # 凭证信息
    voucher_no: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="凭证号（银行流水号/支付宝订单号等）"
    )

    # 备注
    remark: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    # 关联订单（多对一）
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="payments"
    )

    def __repr__(self) -> str:
        return f"<OrderPayment(payment_no='{self.payment_no}', amount={self.payment_amount}, method={self.payment_method})>"
