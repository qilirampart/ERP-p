"""
收款管理业务逻辑Service层
"""
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from app.models.payment import OrderPayment, PaymentMethod, PaymentStatus
from app.models.order import Order
from app.schemas.payment import OrderPaymentCreate, OrderPaymentUpdate, OrderPaymentSummary


async def generate_payment_no(db: AsyncSession) -> str:
    """
    生成收款单号
    格式: PAY+YYYYMMDD+001
    """
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"PAY{today_str}"

    # 查询今天已有的最大序号
    stmt = select(OrderPayment.payment_no).where(
        OrderPayment.payment_no.like(f"{prefix}%")
    ).order_by(OrderPayment.payment_no.desc())

    result = await db.execute(stmt)
    last_no = result.scalar()

    if last_no:
        # 提取序号并+1
        seq = int(last_no[-6:]) + 1
    else:
        seq = 1

    return f"{prefix}{seq:06d}"


async def create_order_payment(db: AsyncSession, data: OrderPaymentCreate) -> OrderPayment:
    """
    创建收款记录
    1. 验证订单存在
    2. 生成收款单号
    3. 创建收款记录
    4. 确认状态
    """
    # 1. 验证订单存在
    stmt = select(Order).where(Order.id == data.order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError("订单不存在")

    # 2. 生成收款单号
    payment_no = await generate_payment_no(db)

    # 3. 创建收款记录
    payment = OrderPayment(
        order_id=data.order_id,
        payment_no=payment_no,
        payment_amount=data.payment_amount,
        payment_method=PaymentMethod(data.payment_method),
        payment_date=data.payment_date,
        status=PaymentStatus.CONFIRMED,  # 默认已确认
        received_by=data.received_by,
        voucher_no=data.voucher_no,
        remark=data.remark
    )
    db.add(payment)

    await db.commit()
    await db.refresh(payment)

    return payment


async def get_order_payments(
    db: AsyncSession,
    order_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[dict]:
    """
    获取收款记录列表
    """
    stmt = (
        select(OrderPayment, Order.order_no, Order.customer_name)
        .join(Order, OrderPayment.order_id == Order.id)
    )

    if order_id:
        stmt = stmt.where(OrderPayment.order_id == order_id)

    if status:
        stmt = stmt.where(OrderPayment.status == status)

    stmt = stmt.order_by(OrderPayment.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    # 组装返回数据
    payment_list = []
    for row in rows:
        payment = row[0]
        order_no = row[1]
        customer_name = row[2]

        payment_list.append({
            "id": payment.id,
            "order_id": payment.order_id,
            "order_no": order_no,
            "customer_name": customer_name,
            "payment_no": payment.payment_no,
            "payment_amount": payment.payment_amount,
            "payment_method": payment.payment_method.value,
            "payment_date": payment.payment_date,
            "status": payment.status.value,
            "received_by": payment.received_by,
            "voucher_no": payment.voucher_no,
            "remark": payment.remark,
            "created_at": payment.created_at,
            "updated_at": payment.updated_at
        })

    return payment_list


async def get_order_payment_detail(db: AsyncSession, payment_id: int) -> OrderPayment:
    """
    获取收款记录详情
    """
    stmt = (
        select(OrderPayment)
        .where(OrderPayment.id == payment_id)
        .options(selectinload(OrderPayment.order))
    )

    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        raise ValueError("收款记录不存在")

    return payment


async def update_order_payment(
    db: AsyncSession,
    payment_id: int,
    data: OrderPaymentUpdate
) -> OrderPayment:
    """
    更新收款记录
    """
    stmt = select(OrderPayment).where(OrderPayment.id == payment_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        raise ValueError("收款记录不存在")

    if payment.status == PaymentStatus.CANCELLED:
        raise ValueError("已取消的收款记录不能修改")

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "payment_method" and value:
            setattr(payment, key, PaymentMethod(value))
        else:
            setattr(payment, key, value)

    payment.updated_at = datetime.now()

    await db.commit()
    await db.refresh(payment)

    return payment


async def cancel_order_payment(db: AsyncSession, payment_id: int, reason: str):
    """
    取消收款记录
    """
    stmt = select(OrderPayment).where(OrderPayment.id == payment_id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        raise ValueError("收款记录不存在")

    if payment.status == PaymentStatus.CANCELLED:
        raise ValueError("收款记录已经是取消状态")

    payment.status = PaymentStatus.CANCELLED
    payment.updated_at = datetime.now()

    # 将取消原因追加到备注中
    if payment.remark:
        payment.remark = f"{payment.remark}\n取消原因: {reason}"
    else:
        payment.remark = f"取消原因: {reason}"

    await db.commit()
    await db.refresh(payment)

    return payment


async def get_order_payment_summary(db: AsyncSession, order_id: int) -> OrderPaymentSummary:
    """
    获取订单收款汇总信息
    """
    # 查询订单信息
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError("订单不存在")

    # 查询已收款金额（只统计已确认的收款）
    stmt = (
        select(func.sum(OrderPayment.payment_amount))
        .where(
            and_(
                OrderPayment.order_id == order_id,
                OrderPayment.status == PaymentStatus.CONFIRMED
            )
        )
    )
    result = await db.execute(stmt)
    paid_amount = result.scalar() or Decimal("0.00")

    # 查询收款次数
    stmt = (
        select(func.count(OrderPayment.id))
        .where(
            and_(
                OrderPayment.order_id == order_id,
                OrderPayment.status == PaymentStatus.CONFIRMED
            )
        )
    )
    result = await db.execute(stmt)
    payment_count = result.scalar() or 0

    # 计算未收款金额
    unpaid_amount = order.total_amount - paid_amount

    # 确定收款状态
    if paid_amount == 0:
        payment_status = "UNPAID"  # 未收款
    elif paid_amount >= order.total_amount:
        payment_status = "PAID"    # 已收款
    else:
        payment_status = "PARTIAL" # 部分收款

    return OrderPaymentSummary(
        order_id=order.id,
        order_no=order.order_no,
        customer_name=order.customer_name,
        total_amount=order.total_amount,
        paid_amount=paid_amount,
        unpaid_amount=unpaid_amount,
        payment_count=payment_count,
        payment_status=payment_status
    )


async def get_payment_statistics(db: AsyncSession):
    """
    获取收款统计数据
    """
    # 总收款记录数
    total_stmt = select(func.count(OrderPayment.id))
    total_result = await db.execute(total_stmt)
    total_count = total_result.scalar() or 0

    # 总收款金额（已确认）
    amount_stmt = (
        select(func.sum(OrderPayment.payment_amount))
        .where(OrderPayment.status == PaymentStatus.CONFIRMED)
    )
    amount_result = await db.execute(amount_stmt)
    total_amount = amount_result.scalar() or Decimal("0.00")

    # 今日收款金额
    today = datetime.now().date()
    today_stmt = (
        select(func.sum(OrderPayment.payment_amount))
        .where(
            and_(
                OrderPayment.status == PaymentStatus.CONFIRMED,
                func.date(OrderPayment.payment_date) == today
            )
        )
    )
    today_result = await db.execute(today_stmt)
    today_amount = today_result.scalar() or Decimal("0.00")

    # 各收款方式统计
    method_stmt = (
        select(OrderPayment.payment_method, func.sum(OrderPayment.payment_amount))
        .where(OrderPayment.status == PaymentStatus.CONFIRMED)
        .group_by(OrderPayment.payment_method)
    )
    method_result = await db.execute(method_stmt)
    method_stats = {row[0].value: float(row[1]) for row in method_result.all()}

    return {
        "total_payment_count": total_count,
        "total_payment_amount": float(total_amount),
        "today_payment_amount": float(today_amount),
        "payment_method_stats": method_stats
    }
