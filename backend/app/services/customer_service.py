"""
客户业务逻辑服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

from app.models.customer import Customer, CustomerLevel, CustomerStatus
from app.models.order import Order, OrderStatus
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerStatistics


async def generate_customer_code(db: AsyncSession) -> str:
    """
    生成客户编号
    格式: CUS + YYYYMMDD + 3位序号
    示例: CUS20251223001
    """
    today = date.today()
    prefix = f"CUS{today.strftime('%Y%m%d')}"

    # 查询今天已有的最大序号
    stmt = select(func.max(Customer.customer_code)).where(
        Customer.customer_code.like(f"{prefix}%")
    )
    result = await db.execute(stmt)
    max_code = result.scalar()

    if max_code:
        # 提取序号并加1
        seq = int(max_code[-3:]) + 1
    else:
        seq = 1

    return f"{prefix}{seq:03d}"


async def create_customer(db: AsyncSession, customer_data: CustomerCreate) -> Customer:
    """创建客户"""
    # 检查客户名称是否重复
    stmt = select(Customer).where(Customer.customer_name == customer_data.customer_name)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise ValueError(f"客户名称 '{customer_data.customer_name}' 已存在")

    # 生成客户编号
    customer_code = await generate_customer_code(db)

    # 创建客户
    customer = Customer(
        customer_code=customer_code,
        **customer_data.model_dump()
    )

    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    return customer


async def get_customer(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    """获取客户详情"""
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_customers(
    db: AsyncSession,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    customer_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Customer]:
    """
    获取客户列表
    支持搜索、筛选、分页
    """
    stmt = select(Customer)

    # 搜索条件
    if keyword:
        search_filter = or_(
            Customer.customer_name.like(f"%{keyword}%"),
            Customer.customer_code.like(f"%{keyword}%"),
            Customer.contact_person.like(f"%{keyword}%"),
            Customer.contact_phone.like(f"%{keyword}%")
        )
        stmt = stmt.where(search_filter)

    # 状态筛选
    if status:
        stmt = stmt.where(Customer.status == status)

    # 客户等级筛选
    if customer_level:
        stmt = stmt.where(Customer.customer_level == customer_level)

    # 排序：等级升序，创建时间降序
    stmt = stmt.order_by(
        Customer.customer_level.asc(),
        Customer.created_at.desc()
    )

    # 分页
    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()


async def update_customer(
    db: AsyncSession,
    customer_id: int,
    customer_data: CustomerUpdate
) -> Customer:
    """更新客户信息"""
    customer = await get_customer(db, customer_id)
    if not customer:
        raise ValueError(f"客户 ID {customer_id} 不存在")

    # 如果更新客户名称，检查是否重复
    if customer_data.customer_name and customer_data.customer_name != customer.customer_name:
        stmt = select(Customer).where(
            and_(
                Customer.customer_name == customer_data.customer_name,
                Customer.id != customer_id
            )
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError(f"客户名称 '{customer_data.customer_name}' 已存在")

    # 更新字段
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    await db.commit()
    await db.refresh(customer)

    return customer


async def delete_customer(db: AsyncSession, customer_id: int) -> None:
    """删除客户"""
    customer = await get_customer(db, customer_id)
    if not customer:
        raise ValueError(f"客户 ID {customer_id} 不存在")

    # 检查是否有关联订单
    stmt = select(func.count(Order.id)).where(Order.customer_id == customer_id)
    result = await db.execute(stmt)
    order_count = result.scalar()

    if order_count > 0:
        raise ValueError(f"该客户有 {order_count} 个关联订单，无法删除")

    await db.delete(customer)
    await db.commit()


async def get_customer_statistics(
    db: AsyncSession,
    customer_id: int
) -> CustomerStatistics:
    """获取客户统计信息"""
    # 总订单数
    total_orders_stmt = select(func.count(Order.id)).where(
        Order.customer_id == customer_id
    )
    total_orders = (await db.execute(total_orders_stmt)).scalar() or 0

    # 总交易额
    total_amount_stmt = select(func.sum(Order.total_amount)).where(
        Order.customer_id == customer_id
    )
    total_amount = (await db.execute(total_amount_stmt)).scalar() or Decimal("0.00")

    # 已完成订单数
    completed_orders_stmt = select(func.count(Order.id)).where(
        and_(
            Order.customer_id == customer_id,
            Order.status == OrderStatus.COMPLETED
        )
    )
    completed_orders = (await db.execute(completed_orders_stmt)).scalar() or 0

    # 平均订单金额
    if total_orders > 0:
        average_order_amount = total_amount / total_orders
    else:
        average_order_amount = Decimal("0.00")

    # 最近订单日期
    last_order_stmt = select(func.max(Order.created_at)).where(
        Order.customer_id == customer_id
    )
    last_order_date = (await db.execute(last_order_stmt)).scalar()

    return CustomerStatistics(
        total_orders=total_orders,
        total_amount=total_amount,
        completed_orders=completed_orders,
        average_order_amount=average_order_amount,
        last_order_date=last_order_date
    )


async def get_customer_orders(
    db: AsyncSession,
    customer_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[Order]:
    """获取客户历史订单"""
    stmt = (
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()
