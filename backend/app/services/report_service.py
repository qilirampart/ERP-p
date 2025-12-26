"""
财务报表业务逻辑Service层
"""
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from typing import List, Optional
from decimal import Decimal

from app.models.payment import OrderPayment, PaymentMethod, PaymentStatus
from app.models.order import Order
from app.schemas.report import (
    DailyPaymentReport,
    MonthlyPaymentReport,
    CustomerReceivable,
    CustomerReceivableSummary,
    DailyTrend,
    SalesPaymentTrend,
    AgingBracket,
    ReceivablesAgingAnalysis,
    FinancialOverview
)


# ==================== 收款日报 ====================

async def get_daily_payment_report(
    db: AsyncSession,
    start_date: date,
    end_date: date
) -> List[DailyPaymentReport]:
    """
    获取收款日报
    按日期范围查询，返回每日收款汇总
    """
    # 构建查询：按日期和收款方式分组统计
    stmt = select(
        func.date(OrderPayment.payment_date).label('date'),
        func.count(OrderPayment.id).label('payment_count'),
        func.sum(OrderPayment.payment_amount).label('total_amount'),
        func.sum(
            case((OrderPayment.payment_method == PaymentMethod.CASH, OrderPayment.payment_amount), else_=0)
        ).label('cash_amount'),
        func.sum(
            case((OrderPayment.payment_method == PaymentMethod.BANK_TRANSFER, OrderPayment.payment_amount), else_=0)
        ).label('bank_transfer_amount'),
        func.sum(
            case((OrderPayment.payment_method == PaymentMethod.ALIPAY, OrderPayment.payment_amount), else_=0)
        ).label('alipay_amount'),
        func.sum(
            case((OrderPayment.payment_method == PaymentMethod.WECHAT, OrderPayment.payment_amount), else_=0)
        ).label('wechat_amount'),
        func.sum(
            case((OrderPayment.payment_method == PaymentMethod.CHECK, OrderPayment.payment_amount), else_=0)
        ).label('check_amount'),
        func.sum(
            case((OrderPayment.payment_method == PaymentMethod.OTHER, OrderPayment.payment_amount), else_=0)
        ).label('other_amount'),
    ).where(
        and_(
            func.date(OrderPayment.payment_date) >= start_date,
            func.date(OrderPayment.payment_date) <= end_date,
            OrderPayment.status == PaymentStatus.CONFIRMED
        )
    ).group_by(
        func.date(OrderPayment.payment_date)
    ).order_by(
        func.date(OrderPayment.payment_date)
    )

    result = await db.execute(stmt)
    rows = result.all()

    # 转换为报表对象
    reports = []
    for row in rows:
        reports.append(DailyPaymentReport(
            date=row.date,
            payment_count=row.payment_count or 0,
            total_amount=row.total_amount or Decimal("0.00"),
            cash_amount=row.cash_amount or Decimal("0.00"),
            bank_transfer_amount=row.bank_transfer_amount or Decimal("0.00"),
            alipay_amount=row.alipay_amount or Decimal("0.00"),
            wechat_amount=row.wechat_amount or Decimal("0.00"),
            check_amount=row.check_amount or Decimal("0.00"),
            other_amount=row.other_amount or Decimal("0.00")
        ))

    return reports


# ==================== 收款月报 ====================

async def get_monthly_payment_report(
    db: AsyncSession,
    year: int,
    month: int
) -> MonthlyPaymentReport:
    """
    获取收款月报
    指定年月，返回当月收款汇总和环比增长率
    """
    # 计算当月日期范围
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
        last_month_start = date(year, 11, 1)
        last_month_end = date(year, 12, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
        if month == 1:
            last_month_start = date(year - 1, 12, 1)
            last_month_end = date(year, 1, 1) - timedelta(days=1)
        else:
            last_month_start = date(year, month - 1, 1)
            last_month_end = date(year, month, 1) - timedelta(days=1)

    # 查询当月数据
    stmt = select(
        func.count(OrderPayment.id).label('payment_count'),
        func.sum(OrderPayment.payment_amount).label('total_amount'),
        OrderPayment.payment_method
    ).where(
        and_(
            func.date(OrderPayment.payment_date) >= start_date,
            func.date(OrderPayment.payment_date) <= end_date,
            OrderPayment.status == PaymentStatus.CONFIRMED
        )
    ).group_by(
        OrderPayment.payment_method
    )

    result = await db.execute(stmt)
    rows = result.all()

    # 汇总数据
    payment_count = 0
    total_amount = Decimal("0.00")
    payment_methods = {}

    for row in rows:
        payment_count += row.payment_count or 0
        amount = row.total_amount or Decimal("0.00")
        total_amount += amount
        payment_methods[row.payment_method.value] = float(amount)

    # 计算平均金额
    average_amount = total_amount / payment_count if payment_count > 0 else Decimal("0.00")

    # 查询上月总额用于计算环比
    stmt_last = select(
        func.sum(OrderPayment.payment_amount)
    ).where(
        and_(
            func.date(OrderPayment.payment_date) >= last_month_start,
            func.date(OrderPayment.payment_date) <= last_month_end,
            OrderPayment.status == PaymentStatus.CONFIRMED
        )
    )

    result_last = await db.execute(stmt_last)
    last_month_amount = result_last.scalar() or Decimal("0.00")

    # 计算环比增长率
    growth_rate = None
    if last_month_amount > 0:
        growth_rate = ((total_amount - last_month_amount) / last_month_amount * 100).quantize(Decimal("0.01"))

    return MonthlyPaymentReport(
        year=year,
        month=month,
        payment_count=payment_count,
        total_amount=total_amount,
        average_amount=average_amount,
        growth_rate=growth_rate,
        payment_methods=payment_methods
    )


# ==================== 客户欠款统计 ====================

async def get_customer_receivables(db: AsyncSession) -> CustomerReceivableSummary:
    """
    获取客户欠款统计
    返回所有客户的订单总额、已收款、欠款信息
    """
    # 子查询：每个订单的已收款金额
    subq_paid = select(
        OrderPayment.order_id,
        func.sum(OrderPayment.payment_amount).label('paid_amount')
    ).where(
        OrderPayment.status == PaymentStatus.CONFIRMED
    ).group_by(
        OrderPayment.order_id
    ).subquery()

    # 主查询：按客户汇总
    stmt = select(
        Order.customer_id,
        Order.customer_name,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('total_order_amount'),
        func.coalesce(func.sum(subq_paid.c.paid_amount), 0).label('paid_amount'),
        func.min(Order.created_at).label('earliest_date')
    ).outerjoin(
        subq_paid, Order.id == subq_paid.c.order_id
    ).where(
        Order.customer_id.is_not(None)
    ).group_by(
        Order.customer_id,
        Order.customer_name
    ).order_by(
        func.sum(Order.total_amount) - func.coalesce(func.sum(subq_paid.c.paid_amount), 0).desc()
    )

    result = await db.execute(stmt)
    rows = result.all()

    # 转换为客户欠款对象
    customers = []
    total_receivable = Decimal("0.00")
    total_paid = Decimal("0.00")
    total_unpaid = Decimal("0.00")
    unpaid_customer_count = 0

    for row in rows:
        total_amount = row.total_order_amount or Decimal("0.00")
        paid = row.paid_amount or Decimal("0.00")
        unpaid = total_amount - paid

        total_receivable += total_amount
        total_paid += paid
        total_unpaid += unpaid

        if unpaid > 0:
            unpaid_customer_count += 1

        # 查询该客户有欠款的订单数
        stmt_unpaid_orders = select(
            func.count(Order.id)
        ).outerjoin(
            subq_paid, Order.id == subq_paid.c.order_id
        ).where(
            and_(
                Order.customer_id == row.customer_id,
                Order.total_amount > func.coalesce(subq_paid.c.paid_amount, 0)
            )
        )
        result_unpaid = await db.execute(stmt_unpaid_orders)
        unpaid_order_count = result_unpaid.scalar() or 0

        customers.append(CustomerReceivable(
            customer_id=row.customer_id,
            customer_name=row.customer_name,
            total_order_amount=total_amount,
            paid_amount=paid,
            unpaid_amount=unpaid,
            order_count=row.order_count or 0,
            unpaid_order_count=unpaid_order_count,
            earliest_unpaid_date=row.earliest_date if unpaid > 0 else None
        ))

    return CustomerReceivableSummary(
        total_receivable=total_receivable,
        total_paid=total_paid,
        total_unpaid=total_unpaid,
        customer_count=len(customers),
        unpaid_customer_count=unpaid_customer_count,
        customers=customers
    )


# ==================== 销售收款趋势 ====================

async def get_sales_payment_trend(
    db: AsyncSession,
    days: int = 30
) -> SalesPaymentTrend:
    """
    获取销售收款趋势
    返回指定天数内的每日订单和收款数据
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # 查询每日订单数据
    stmt_orders = select(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('order_amount'),
        func.count(Order.id).label('order_count')
    ).where(
        func.date(Order.created_at) >= start_date
    ).group_by(
        func.date(Order.created_at)
    )

    result_orders = await db.execute(stmt_orders)
    orders_dict = {row.date: row for row in result_orders.all()}

    # 查询每日收款数据
    stmt_payments = select(
        func.date(OrderPayment.payment_date).label('date'),
        func.sum(OrderPayment.payment_amount).label('payment_amount'),
        func.count(OrderPayment.id).label('payment_count')
    ).where(
        and_(
            func.date(OrderPayment.payment_date) >= start_date,
            OrderPayment.status == PaymentStatus.CONFIRMED
        )
    ).group_by(
        func.date(OrderPayment.payment_date)
    )

    result_payments = await db.execute(stmt_payments)
    payments_dict = {row.date: row for row in result_payments.all()}

    # 合并数据，生成每日趋势
    daily_data = []
    total_order_amount = Decimal("0.00")
    total_payment_amount = Decimal("0.00")
    total_order_count = 0
    total_payment_count = 0

    current_date = start_date
    while current_date <= end_date:
        order_row = orders_dict.get(current_date)
        payment_row = payments_dict.get(current_date)

        order_amount = order_row.order_amount if order_row else Decimal("0.00")
        payment_amount = payment_row.payment_amount if payment_row else Decimal("0.00")
        order_count = order_row.order_count if order_row else 0
        payment_count = payment_row.payment_count if payment_row else 0

        daily_data.append(DailyTrend(
            date=current_date,
            order_amount=order_amount or Decimal("0.00"),
            payment_amount=payment_amount or Decimal("0.00"),
            order_count=order_count or 0,
            payment_count=payment_count or 0
        ))

        total_order_amount += order_amount or Decimal("0.00")
        total_payment_amount += payment_amount or Decimal("0.00")
        total_order_count += order_count or 0
        total_payment_count += payment_count or 0

        current_date += timedelta(days=1)

    return SalesPaymentTrend(
        start_date=start_date,
        end_date=end_date,
        total_order_amount=total_order_amount,
        total_payment_amount=total_payment_amount,
        total_order_count=total_order_count,
        total_payment_count=total_payment_count,
        daily_data=daily_data
    )


# ==================== 应收账款账龄分析 ====================

async def get_receivables_aging_analysis(db: AsyncSession) -> ReceivablesAgingAnalysis:
    """
    获取应收账款账龄分析
    按账龄区间统计未收款金额
    """
    today = date.today()

    # 子查询：每个订单的已收款金额
    subq_paid = select(
        OrderPayment.order_id,
        func.sum(OrderPayment.payment_amount).label('paid_amount')
    ).where(
        OrderPayment.status == PaymentStatus.CONFIRMED
    ).group_by(
        OrderPayment.order_id
    ).subquery()

    # 查询所有有欠款的订单
    stmt = select(
        Order.id,
        Order.order_no,
        Order.total_amount,
        func.coalesce(subq_paid.c.paid_amount, 0).label('paid_amount'),
        Order.created_at
    ).outerjoin(
        subq_paid, Order.id == subq_paid.c.order_id
    ).where(
        Order.total_amount > func.coalesce(subq_paid.c.paid_amount, 0)
    )

    result = await db.execute(stmt)
    rows = result.all()

    # 初始化账龄区间
    brackets = {
        '0-7': {'amount': Decimal("0.00"), 'count': 0, 'name': '0-7天', 'range': '0-7天'},
        '8-30': {'amount': Decimal("0.00"), 'count': 0, 'name': '8-30天', 'range': '8-30天'},
        '31-60': {'amount': Decimal("0.00"), 'count': 0, 'name': '31-60天', 'range': '31-60天'},
        '61-90': {'amount': Decimal("0.00"), 'count': 0, 'name': '61-90天', 'range': '61-90天'},
        '90+': {'amount': Decimal("0.00"), 'count': 0, 'name': '90天以上', 'range': '90天+'}
    }

    total_receivable = Decimal("0.00")

    # 按账龄分类统计
    for row in rows:
        unpaid_amount = row.total_amount - (row.paid_amount or Decimal("0.00"))
        days_old = (today - row.created_at.date()).days

        total_receivable += unpaid_amount

        if days_old <= 7:
            brackets['0-7']['amount'] += unpaid_amount
            brackets['0-7']['count'] += 1
        elif days_old <= 30:
            brackets['8-30']['amount'] += unpaid_amount
            brackets['8-30']['count'] += 1
        elif days_old <= 60:
            brackets['31-60']['amount'] += unpaid_amount
            brackets['31-60']['count'] += 1
        elif days_old <= 90:
            brackets['61-90']['amount'] += unpaid_amount
            brackets['61-90']['count'] += 1
        else:
            brackets['90+']['amount'] += unpaid_amount
            brackets['90+']['count'] += 1

    # 计算百分比
    aging_brackets = []
    for key, data in brackets.items():
        percentage = (data['amount'] / total_receivable * 100).quantize(Decimal("0.01")) if total_receivable > 0 else Decimal("0.00")
        aging_brackets.append(AgingBracket(
            bracket_name=data['name'],
            days_range=data['range'],
            amount=data['amount'],
            order_count=data['count'],
            percentage=percentage
        ))

    return ReceivablesAgingAnalysis(
        total_receivable=total_receivable,
        aging_brackets=aging_brackets,
        bracket_0_7=aging_brackets[0],
        bracket_8_30=aging_brackets[1],
        bracket_31_60=aging_brackets[2],
        bracket_61_90=aging_brackets[3],
        bracket_90_plus=aging_brackets[4]
    )


# ==================== 综合财务概览 ====================

async def get_financial_overview(db: AsyncSession) -> FinancialOverview:
    """
    获取综合财务概览
    汇总订单、收款、应收款等关键指标
    """
    # 查询订单统计
    stmt_orders = select(
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total_amount).label('total_order_amount'),
        func.sum(case((Order.status == 'COMPLETED', 1), else_=0)).label('completed_orders')
    )
    result_orders = await db.execute(stmt_orders)
    orders_data = result_orders.first()

    # 查询收款统计
    stmt_payments = select(
        func.count(OrderPayment.id).label('total_payments'),
        func.sum(OrderPayment.payment_amount).label('total_payment_amount')
    ).where(
        OrderPayment.status == PaymentStatus.CONFIRMED
    )
    result_payments = await db.execute(stmt_payments)
    payments_data = result_payments.first()

    total_order_amount = orders_data.total_order_amount or Decimal("0.00")
    total_payment_amount = payments_data.total_payment_amount or Decimal("0.00")
    total_receivable = total_order_amount - total_payment_amount

    # 计算回款率
    payment_rate = (total_payment_amount / total_order_amount * 100).quantize(Decimal("0.01")) if total_order_amount > 0 else Decimal("0.00")

    # 查询逾期金额（30天以上未收款）
    overdue_date = datetime.now() - timedelta(days=30)

    subq_paid = select(
        OrderPayment.order_id,
        func.sum(OrderPayment.payment_amount).label('paid_amount')
    ).where(
        OrderPayment.status == PaymentStatus.CONFIRMED
    ).group_by(
        OrderPayment.order_id
    ).subquery()

    stmt_overdue = select(
        func.sum(Order.total_amount - func.coalesce(subq_paid.c.paid_amount, 0)).label('overdue_amount'),
        func.count(Order.id).label('overdue_count')
    ).outerjoin(
        subq_paid, Order.id == subq_paid.c.order_id
    ).where(
        and_(
            Order.created_at < overdue_date,
            Order.total_amount > func.coalesce(subq_paid.c.paid_amount, 0)
        )
    )
    result_overdue = await db.execute(stmt_overdue)
    overdue_data = result_overdue.first()

    # 本月统计
    month_start = date.today().replace(day=1)

    stmt_month_orders = select(
        func.sum(Order.total_amount).label('month_order_amount'),
        func.count(Order.id).label('month_order_count')
    ).where(
        func.date(Order.created_at) >= month_start
    )
    result_month_orders = await db.execute(stmt_month_orders)
    month_orders_data = result_month_orders.first()

    stmt_month_payments = select(
        func.sum(OrderPayment.payment_amount).label('month_payment_amount'),
        func.count(OrderPayment.id).label('month_payment_count')
    ).where(
        and_(
            func.date(OrderPayment.payment_date) >= month_start,
            OrderPayment.status == PaymentStatus.CONFIRMED
        )
    )
    result_month_payments = await db.execute(stmt_month_payments)
    month_payments_data = result_month_payments.first()

    return FinancialOverview(
        total_orders=orders_data.total_orders or 0,
        total_order_amount=total_order_amount,
        completed_orders=orders_data.completed_orders or 0,
        total_payments=payments_data.total_payments or 0,
        total_payment_amount=total_payment_amount,
        payment_rate=payment_rate,
        total_receivable=total_receivable,
        overdue_amount=overdue_data.overdue_amount or Decimal("0.00"),
        overdue_count=overdue_data.overdue_count or 0,
        month_order_amount=month_orders_data.month_order_amount or Decimal("0.00"),
        month_payment_amount=month_payments_data.month_payment_amount or Decimal("0.00"),
        month_order_count=month_orders_data.month_order_count or 0,
        month_payment_count=month_payments_data.month_payment_count or 0
    )
