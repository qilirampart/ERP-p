"""
订单管理路由 - CRUD + 智能计算 + Excel导出
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.material import Material
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse
)
from app.schemas.response import success_response, error_response
from app.services.calculation_service import CalculationService
from app.utils.excel_handler import ExcelHandler

router = APIRouter()


def generate_order_no() -> str:
    """生成订单编号: SO+YYYYMMDD+001"""
    today = datetime.now().strftime("%Y%m%d")
    # TODO: 实现自增逻辑，这里简化为时间戳
    timestamp = datetime.now().strftime("%H%M%S")
    return f"SO{today}{timestamp}"


@router.post("/", response_model=dict, summary="创建订单")
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    创建订单并自动计算报价

    系统会自动：
    1. 为每个订单明细计算开纸方案
    2. 计算纸张消耗
    3. 计算明细金额
    4. 汇总订单总金额
    """
    try:
        # 创建订单主表
        order = Order(
            order_no=generate_order_no(),
            customer_name=order_in.customer_name,
            contact_person=order_in.contact_person,
            contact_phone=order_in.contact_phone,
            remark=order_in.remark,
            status=OrderStatus.DRAFT
        )
        db.add(order)
        await db.flush()  # 获取order.id

        total_amount = Decimal("0.00")

        # 处理每个订单明细
        for item_data in order_in.items:
            # 查询纸张信息
            result = await db.execute(
                select(Material).where(Material.id == item_data.paper_material_id)
            )
            paper = result.scalar_one_or_none()

            if not paper or paper.category.value != "PAPER":
                raise ValueError(f"纸张ID {item_data.paper_material_id} 无效")

            # 计算开纸方案
            cut_result = CalculationService.calculate_max_cut(
                paper_w=paper.spec_width,
                paper_h=paper.spec_length,
                target_w=item_data.finished_size_w,
                target_h=item_data.finished_size_h
            )

            if cut_result["count"] == 0:
                raise ValueError(
                    f"产品 '{item_data.product_name}' 尺寸超出纸张规格，无法开纸"
                )

            # 计算报价
            quote_result = CalculationService.calculate_quote(
                quantity=item_data.quantity,
                page_count=item_data.page_count,
                paper_cost_per_sheet=paper.cost_price,
                cut_result=cut_result
            )

            # 创建订单明细
            order_item = OrderItem(
                order_id=order.id,
                product_name=item_data.product_name,
                quantity=item_data.quantity,
                finished_size_w=item_data.finished_size_w,
                finished_size_h=item_data.finished_size_h,
                page_count=item_data.page_count,
                paper_material_id=item_data.paper_material_id,
                crafts=item_data.crafts,
                paper_usage=quote_result["paper_usage"],
                cut_method=cut_result["method"],
                item_amount=quote_result["total_cost"]
            )
            db.add(order_item)

            total_amount += quote_result["total_cost"]

        # 更新订单总金额
        order.total_amount = total_amount
        await db.commit()
        await db.refresh(order)

        # 加载关联数据
        result = await db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order.id)
        )
        order_with_items = result.scalar_one()

        return success_response(
            data=OrderResponse.model_validate(order_with_items).model_dump(),
            msg="订单创建成功"
        )

    except ValueError as e:
        await db.rollback()
        return error_response(str(e), code=400)
    except Exception as e:
        await db.rollback()
        return error_response(f"创建订单失败: {str(e)}", code=500)


@router.get("/", response_model=dict, summary="获取订单列表")
async def list_orders(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    customer_name: str = None,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """获取订单列表（支持分页和筛选）"""
    query = select(Order, func.count(OrderItem.id).label("items_count")).outerjoin(
        OrderItem, Order.id == OrderItem.order_id
    ).group_by(Order.id)

    if status:
        query = query.where(Order.status == status)

    if customer_name:
        query = query.where(Order.customer_name.like(f"%{customer_name}%"))

    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    orders_list = []
    for order, items_count in rows:
        order_dict = OrderListResponse.model_validate(order).model_dump()
        order_dict["items_count"] = items_count
        orders_list.append(order_dict)

    return success_response(data=orders_list)


@router.get("/{order_id}", response_model=dict, summary="获取订单详情")
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """获取订单详情（含明细）"""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        return error_response(f"订单ID {order_id} 不存在", code=404)

    return success_response(
        data=OrderResponse.model_validate(order).model_dump()
    )


@router.put("/{order_id}", response_model=dict, summary="更新订单")
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """更新订单信息（不含明细）"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        return error_response(f"订单ID {order_id} 不存在", code=404)

    # 更新字段
    update_data = order_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)

    await db.commit()
    await db.refresh(order)

    return success_response(
        data=OrderResponse.model_validate(order).model_dump(),
        msg="订单更新成功"
    )


@router.post("/{order_id}/confirm", response_model=dict, summary="确认订单")
async def confirm_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """确认订单（状态：DRAFT -> CONFIRMED）"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        return error_response(f"订单ID {order_id} 不存在", code=404)

    if order.status != OrderStatus.DRAFT:
        return error_response(f"订单状态为 {order.status.value}，无法确认", code=400)

    order.status = OrderStatus.CONFIRMED
    await db.commit()

    return success_response(msg="订单已确认")


@router.delete("/{order_id}", response_model=dict, summary="删除订单")
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """删除订单（仅草稿状态可删除）"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        return error_response(f"订单ID {order_id} 不存在", code=404)

    if order.status != OrderStatus.DRAFT:
        return error_response("仅草稿状态的订单可删除", code=400)

    await db.delete(order)
    await db.commit()

    return success_response(msg="订单已删除")


# ==================== Excel导出功能 ====================

@router.get("/excel/export", summary="导出订单数据到Excel")
async def export_orders_to_excel(
    status: Optional[str] = Query(None, description="订单状态筛选"),
    customer_name: Optional[str] = Query(None, description="客户名称搜索"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    导出订单数据到Excel

    支持：
    - 按状态筛选
    - 按客户名称搜索
    - 按日期范围筛选
    - 包含订单明细统计
    """
    try:
        # 构建查询
        query = select(
            Order,
            func.count(OrderItem.id).label("items_count")
        ).outerjoin(
            OrderItem, Order.id == OrderItem.order_id
        ).group_by(Order.id)

        # 应用筛选条件
        if status:
            query = query.where(Order.status == status)

        if customer_name:
            query = query.where(Order.customer_name.like(f"%{customer_name}%"))

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.where(Order.created_at >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式错误，应为YYYY-MM-DD")

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                # 包含当天的所有时间
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.where(Order.created_at <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式错误，应为YYYY-MM-DD")

        query = query.order_by(Order.created_at.desc()).limit(10000)

        result = await db.execute(query)
        rows = result.all()

        # 转换为字典列表
        order_data = []
        for order, items_count in rows:
            order_dict = {
                'order_no': order.order_no,
                'customer_name': order.customer_name,
                'contact_person': order.contact_person or '',
                'contact_phone': order.contact_phone or '',
                'status': order.status.value if hasattr(order.status, 'value') else str(order.status),
                'total_amount': float(order.total_amount) if order.total_amount else 0.0,
                'items_count': items_count or 0,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else '',
                'remark': order.remark or ''
            }
            order_data.append(order_dict)

        # 定义导出列
        columns = {
            'order_no': '订单编号',
            'customer_name': '客户名称',
            'contact_person': '联系人',
            'contact_phone': '联系电话',
            'status': '订单状态',
            'total_amount': '订单总额',
            'items_count': '明细数量',
            'created_at': '创建时间',
            'remark': '备注'
        }

        # 生成Excel
        excel_file = ExcelHandler.export_to_excel(
            data=order_data,
            columns=columns,
            sheet_name='订单数据',
            title='订单信息列表'
        )

        # 生成文件名
        filename_parts = ['订单数据']
        if status:
            filename_parts.append(f'{status}')
        if customer_name:
            filename_parts.append(f'{customer_name}')
        filename_parts.append(datetime.now().strftime('%Y%m%d_%H%M%S'))
        filename = '_'.join(filename_parts) + '.xlsx'
        encoded_filename = quote(filename)

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
