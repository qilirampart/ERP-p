"""
仪表盘统计Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.models.order import Order, OrderStatus
from app.models.production import ProductionOrder, ProductionStatus
from app.models.material import Material
from app.models.payment import OrderPayment, PaymentStatus
from app.schemas.dashboard import DashboardStats, RecentOrder, DashboardData


async def get_dashboard_stats(db: AsyncSession) -> DashboardData:
    """
    获取仪表盘统计数据
    """
    today = date.today()
    month_start = date(today.year, today.month, 1)

    # 1. 今日订单统计
    stmt_today_orders = select(
        func.count(Order.id).label('count'),
        func.coalesce(func.sum(Order.total_amount), 0).label('amount')
    ).where(
        func.date(Order.created_at) == today
    )
    result = await db.execute(stmt_today_orders)
    today_orders = result.one()

    # 2. 总订单数
    stmt_total_orders = select(func.count(Order.id))
    total_orders = await db.scalar(stmt_total_orders) or 0

    # 3. 生产统计
    # 生产中
    stmt_production_in_progress = select(func.count(ProductionOrder.id)).where(
        ProductionOrder.status == ProductionStatus.IN_PROGRESS
    )
    production_in_progress = await db.scalar(stmt_production_in_progress) or 0

    # 待生产
    stmt_production_pending = select(func.count(ProductionOrder.id)).where(
        ProductionOrder.status == ProductionStatus.PENDING
    )
    production_pending = await db.scalar(stmt_production_pending) or 0

    # 今日完成
    stmt_production_completed_today = select(func.count(ProductionOrder.id)).where(
        and_(
            ProductionOrder.status == ProductionStatus.COMPLETED,
            func.date(ProductionOrder.actual_end_date) == today
        )
    )
    production_completed_today = await db.scalar(stmt_production_completed_today) or 0

    # 4. 库存预警（低于阈值，暂时设为 < 100）
    stmt_low_stock = select(func.count(Material.id)).where(
        Material.current_stock < 100
    )
    low_stock_count = await db.scalar(stmt_low_stock) or 0

    # 总物料数
    stmt_total_materials = select(func.count(Material.id))
    total_materials_count = await db.scalar(stmt_total_materials) or 0

    # 5. 财务统计
    # 本月收款金额
    stmt_month_payment = select(
        func.coalesce(func.sum(OrderPayment.payment_amount), 0)
    ).where(
        and_(
            OrderPayment.status == PaymentStatus.CONFIRMED,
            OrderPayment.payment_date >= month_start
        )
    )
    month_payment_amount = await db.scalar(stmt_month_payment) or Decimal("0.00")

    # 本月订单金额
    stmt_month_order = select(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).where(
        func.date(Order.created_at) >= month_start
    )
    month_order_amount = await db.scalar(stmt_month_order) or Decimal("0.00")

    # 计算回款率
    if month_order_amount > 0:
        payment_rate = (month_payment_amount / month_order_amount * 100).quantize(Decimal("0.01"))
    else:
        payment_rate = Decimal("0.00")

    # 总应收账款（总订单金额 - 总收款金额）
    stmt_total_order_amount = select(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).where(
        Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.PRODUCTION, OrderStatus.COMPLETED])
    )
    total_order_amount = await db.scalar(stmt_total_order_amount) or Decimal("0.00")

    stmt_total_payment = select(
        func.coalesce(func.sum(OrderPayment.payment_amount), 0)
    ).where(
        OrderPayment.status == PaymentStatus.CONFIRMED
    )
    total_payment = await db.scalar(stmt_total_payment) or Decimal("0.00")

    total_receivable = total_order_amount - total_payment

    # 6. 最近订单（最新10条）
    stmt_recent_orders = (
        select(Order)
        .order_by(Order.created_at.desc())
        .limit(10)
    )
    result = await db.execute(stmt_recent_orders)
    recent_orders_data = result.scalars().all()

    # 构建返回数据
    stats = DashboardStats(
        today_orders_count=today_orders.count,
        today_orders_amount=today_orders.amount,
        total_orders_count=total_orders,
        production_in_progress=production_in_progress,
        production_pending=production_pending,
        production_completed_today=production_completed_today,
        low_stock_count=low_stock_count,
        total_materials_count=total_materials_count,
        month_payment_amount=month_payment_amount,
        month_order_amount=month_order_amount,
        payment_rate=payment_rate,
        total_receivable=total_receivable
    )

    recent_orders = [
        RecentOrder(
            id=order.id,
            order_no=order.order_no,
            customer_name=order.customer_name or "未知客户",
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at
        )
        for order in recent_orders_data
    ]

    return DashboardData(
        stats=stats,
        recent_orders=recent_orders
    )
