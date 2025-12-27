"""
生产工单业务逻辑Service层
"""
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from app.models.production import ProductionOrder, ProductionOrderItem, ProductionReport, ProductionStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.production import ProductionOrderCreate, ProductionOrderUpdate, ProductionReportCreate


async def generate_production_no(db: AsyncSession) -> str:
    """
    生成生产工单号
    格式: PO+YYYYMMDD+001
    """
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"PO{today_str}"

    # 查询今天已有的最大序号
    stmt = select(ProductionOrder.production_no).where(
        ProductionOrder.production_no.like(f"{prefix}%")
    ).order_by(ProductionOrder.production_no.desc()).limit(1)

    result = await db.execute(stmt)
    last_no = result.scalar_one_or_none()

    if last_no:
        # 提取序号并+1
        seq = int(last_no[-6:]) + 1
    else:
        seq = 1

    return f"{prefix}{seq:06d}"


async def create_production_order(db: AsyncSession, data: ProductionOrderCreate) -> ProductionOrder:
    """
    创建生产工单
    1. 检查订单状态（必须是CONFIRMED状态）
    2. 生成工单号
    3. 复制订单明细到生产工单明细
    4. 更新订单状态为PRODUCTION
    """
    # 1. 检查订单
    stmt = select(Order).where(Order.id == data.order_id).options(selectinload(Order.items))
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError("订单不存在")

    if order.status != OrderStatus.CONFIRMED:
        raise ValueError("只能对已确认的订单创建生产工单")

    if not order.items:
        raise ValueError("订单没有明细，无法创建生产工单")

    # 2. 生成工单号
    production_no = await generate_production_no(db)

    # 3. 创建生产工单
    production_order = ProductionOrder(
        production_no=production_no,
        order_id=data.order_id,
        plan_start_date=data.plan_start_date,
        plan_end_date=data.plan_end_date,
        priority=data.priority,
        operator_name=data.operator_name,
        machine_name=data.machine_name,
        remark=data.remark,
        status=ProductionStatus.PENDING
    )
    db.add(production_order)
    await db.flush()  # 获取production_order.id

    # 4. 复制订单明细到生产工单明细
    for order_item in order.items:
        production_item = ProductionOrderItem(
            production_order_id=production_order.id,
            order_item_id=order_item.id,
            product_name=order_item.product_name,
            plan_quantity=order_item.quantity,
            completed_quantity=0,
            rejected_quantity=0,
            finished_size_w=order_item.finished_size_w,
            finished_size_h=order_item.finished_size_h,
            page_count=order_item.page_count,
            paper_material_id=order_item.paper_material_id,
            paper_usage=order_item.paper_usage or 0,
            cut_method=order_item.cut_method or "DIRECT"
        )
        db.add(production_item)

    # 5. 更新订单状态为PRODUCTION
    order.status = OrderStatus.PRODUCTION
    order.updated_at = datetime.now()

    await db.commit()
    await db.refresh(production_order)

    return production_order


async def get_production_orders(
    db: AsyncSession,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    获取生产工单列表
    """
    stmt = (
        select(
            ProductionOrder,
            Order.order_no,
            Order.customer_name,
            func.sum(ProductionOrderItem.plan_quantity).label("total_plan_quantity"),
            func.sum(ProductionOrderItem.completed_quantity).label("total_completed_quantity")
        )
        .join(Order, ProductionOrder.order_id == Order.id)
        .join(ProductionOrderItem, ProductionOrder.id == ProductionOrderItem.production_order_id)
        .group_by(ProductionOrder.id, Order.order_no, Order.customer_name)
    )

    if status:
        stmt = stmt.where(ProductionOrder.status == status)

    stmt = stmt.order_by(
        ProductionOrder.priority.asc(),
        ProductionOrder.created_at.desc()
    ).offset(skip).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    # 组装返回数据
    production_list = []
    for row in rows:
        production_order = row[0]
        order_no = row[1]
        customer_name = row[2]
        total_plan = row[3] or 0
        total_completed = row[4] or 0

        progress_percent = (total_completed / total_plan * 100) if total_plan > 0 else 0

        production_list.append({
            "id": production_order.id,
            "production_no": production_order.production_no,
            "order_id": production_order.order_id,
            "order_no": order_no,
            "customer_name": customer_name,
            "status": production_order.status.value,
            "priority": production_order.priority,
            "plan_start_date": production_order.plan_start_date,
            "plan_end_date": production_order.plan_end_date,
            "operator_name": production_order.operator_name,
            "machine_name": production_order.machine_name,
            "created_at": production_order.created_at,
            "total_plan_quantity": total_plan,
            "total_completed_quantity": total_completed,
            "progress_percent": round(progress_percent, 2)
        })

    return production_list


async def get_production_order_detail(db: AsyncSession, production_id: int):
    """
    获取生产工单详情
    """
    stmt = (
        select(ProductionOrder)
        .where(ProductionOrder.id == production_id)
        .options(
            selectinload(ProductionOrder.order),
            selectinload(ProductionOrder.items)
        )
    )

    result = await db.execute(stmt)
    production_order = result.scalar_one_or_none()

    if not production_order:
        raise ValueError("生产工单不存在")

    return production_order


async def update_production_order(
    db: AsyncSession,
    production_id: int,
    data: ProductionOrderUpdate
) -> ProductionOrder:
    """
    更新生产工单
    """
    stmt = (
        select(ProductionOrder)
        .where(ProductionOrder.id == production_id)
        .options(selectinload(ProductionOrder.order))
    )
    result = await db.execute(stmt)
    production_order = result.scalar_one_or_none()

    if not production_order:
        raise ValueError("生产工单不存在")

    # 记录原始状态
    old_status = production_order.status

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(production_order, key, value)

    production_order.updated_at = datetime.now()

    # 刷新状态
    await db.flush()

    # 如果状态变更为已完成，检查并同步订单状态
    if old_status != ProductionStatus.COMPLETED and production_order.status == ProductionStatus.COMPLETED:
        # 检查该订单的所有生产工单是否都已完成
        stmt_check = select(ProductionOrder).where(
            and_(
                ProductionOrder.order_id == production_order.order_id,
                ProductionOrder.status != ProductionStatus.COMPLETED
            )
        )
        result_check = await db.execute(stmt_check)
        unfinished = result_check.scalars().all()

        # 如果所有工单都完成了，更新订单状态为已完成
        if not unfinished:
            production_order.order.status = OrderStatus.COMPLETED
            production_order.order.updated_at = datetime.now()

    await db.commit()
    await db.refresh(production_order)

    return production_order


async def start_production(db: AsyncSession, production_id: int, operator_name: str):
    """
    开始生产
    """
    stmt = select(ProductionOrder).where(ProductionOrder.id == production_id)
    result = await db.execute(stmt)
    production_order = result.scalar_one_or_none()

    if not production_order:
        raise ValueError("生产工单不存在")

    if production_order.status != ProductionStatus.PENDING:
        raise ValueError("只有待生产状态的工单可以开始生产")

    production_order.status = ProductionStatus.IN_PROGRESS
    production_order.actual_start_date = datetime.now()
    production_order.operator_name = operator_name
    production_order.updated_at = datetime.now()

    # 创建开工报工记录
    report = ProductionReport(
        production_order_id=production_id,
        report_type="START",
        completed_quantity=0,
        rejected_quantity=0,
        operator_name=operator_name,
        remark="开始生产"
    )
    db.add(report)

    await db.commit()
    await db.refresh(production_order)

    return production_order


async def complete_production(db: AsyncSession, production_id: int, operator_name: str):
    """
    完成生产
    """
    stmt = (
        select(ProductionOrder)
        .where(ProductionOrder.id == production_id)
        .options(selectinload(ProductionOrder.order))
    )
    result = await db.execute(stmt)
    production_order = result.scalar_one_or_none()

    if not production_order:
        raise ValueError("生产工单不存在")

    if production_order.status != ProductionStatus.IN_PROGRESS:
        raise ValueError("只有生产中状态的工单可以完成")

    production_order.status = ProductionStatus.COMPLETED
    production_order.actual_end_date = datetime.now()
    production_order.updated_at = datetime.now()

    # 创建完工报工记录
    report = ProductionReport(
        production_order_id=production_id,
        report_type="COMPLETE",
        completed_quantity=0,
        rejected_quantity=0,
        operator_name=operator_name,
        remark="生产完成"
    )
    db.add(report)

    # 刷新数据库状态，确保上面的状态更新在查询时生效
    await db.flush()

    # 检查该订单的所有生产工单是否都已完成
    stmt = select(ProductionOrder).where(
        and_(
            ProductionOrder.order_id == production_order.order_id,
            ProductionOrder.status != ProductionStatus.COMPLETED
        )
    )
    result = await db.execute(stmt)
    unfinished = result.scalars().all()

    # 如果所有工单都完成了，更新订单状态为已完成
    if not unfinished:
        production_order.order.status = OrderStatus.COMPLETED
        production_order.order.updated_at = datetime.now()

    await db.commit()
    await db.refresh(production_order)

    return production_order


async def cancel_production(db: AsyncSession, production_id: int, reason: str):
    """
    取消生产工单
    """
    stmt = select(ProductionOrder).where(ProductionOrder.id == production_id)
    result = await db.execute(stmt)
    production_order = result.scalar_one_or_none()

    if not production_order:
        raise ValueError("生产工单不存在")

    if production_order.status == ProductionStatus.COMPLETED:
        raise ValueError("已完成的工单不能取消")

    if production_order.status == ProductionStatus.CANCELLED:
        raise ValueError("工单已经是取消状态")

    production_order.status = ProductionStatus.CANCELLED
    production_order.updated_at = datetime.now()

    # 将取消原因追加到备注中
    if production_order.remark:
        production_order.remark = f"{production_order.remark}\n取消原因: {reason}"
    else:
        production_order.remark = f"取消原因: {reason}"

    await db.commit()
    await db.refresh(production_order)

    return production_order


async def create_production_report(db: AsyncSession, data: ProductionReportCreate):
    """
    创建生产报工记录
    """
    # 检查生产工单是否存在
    stmt = (
        select(ProductionOrder)
        .where(ProductionOrder.id == data.production_order_id)
        .options(selectinload(ProductionOrder.items))
    )
    result = await db.execute(stmt)
    production_order = result.scalar_one_or_none()

    if not production_order:
        raise ValueError("生产工单不存在")

    # 创建报工记录
    report = ProductionReport(
        production_order_id=data.production_order_id,
        report_type=data.report_type,
        completed_quantity=data.completed_quantity,
        rejected_quantity=data.rejected_quantity,
        operator_name=data.operator_name,
        remark=data.remark
    )
    db.add(report)

    # 更新生产工单明细的完成数量和报废数量
    if data.report_type in ["PROGRESS", "COMPLETE"]:
        for item in production_order.items:
            item.completed_quantity += data.completed_quantity
            if data.report_type == "REJECT" or data.rejected_quantity > 0:
                item.rejected_quantity += data.rejected_quantity

    await db.commit()
    await db.refresh(report)

    return report


async def get_production_reports(db: AsyncSession, production_order_id: int):
    """
    获取生产工单的报工记录
    """
    stmt = (
        select(ProductionReport)
        .where(ProductionReport.production_order_id == production_order_id)
        .order_by(ProductionReport.report_time.desc())
    )

    result = await db.execute(stmt)
    reports = result.scalars().all()

    return reports


async def get_production_statistics(db: AsyncSession):
    """
    获取生产统计数据
    """
    # 总工单数
    total_stmt = select(func.count(ProductionOrder.id))
    total_result = await db.execute(total_stmt)
    total_count = total_result.scalar() or 0

    # 各状态数量
    status_stmt = (
        select(ProductionOrder.status, func.count(ProductionOrder.id))
        .group_by(ProductionOrder.status)
    )
    status_result = await db.execute(status_stmt)
    status_counts = {row[0].value: row[1] for row in status_result.all()}

    # 今日完成数
    today = date.today()
    today_stmt = (
        select(func.count(ProductionOrder.id))
        .where(
            and_(
                ProductionOrder.status == ProductionStatus.COMPLETED,
                func.date(ProductionOrder.actual_end_date) == today
            )
        )
    )
    today_result = await db.execute(today_stmt)
    today_completed = today_result.scalar() or 0

    # 平均完成率
    avg_stmt = (
        select(
            func.avg(
                ProductionOrderItem.completed_quantity * 100.0 / ProductionOrderItem.plan_quantity
            )
        )
        .where(ProductionOrderItem.plan_quantity > 0)
    )
    avg_result = await db.execute(avg_stmt)
    avg_rate = avg_result.scalar() or 0.0

    return {
        "total_production_orders": total_count,
        "pending_count": status_counts.get("PENDING", 0),
        "in_progress_count": status_counts.get("IN_PROGRESS", 0),
        "completed_count": status_counts.get("COMPLETED", 0),
        "today_completed_count": today_completed,
        "avg_completion_rate": round(float(avg_rate), 2)
    }
