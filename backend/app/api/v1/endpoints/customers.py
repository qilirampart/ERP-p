"""
客户管理路由 - CRUD + 统计分析
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListItem,
    CustomerStatistics
)
from app.schemas.order import OrderListResponse
from app.schemas.response import success_response, error_response
from app.services import customer_service

router = APIRouter()


@router.post("/", response_model=dict, summary="创建客户")
async def create_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    创建新客户

    - 自动生成客户编号（格式：CUS20251223001）
    - 客户名称唯一性校验
    - 默认状态为ACTIVE
    """
    try:
        customer = await customer_service.create_customer(db, customer_in)
        return success_response(
            data=CustomerResponse.model_validate(customer).model_dump(),
            msg="客户创建成功"
        )
    except ValueError as e:
        return error_response(str(e), code=400)
    except Exception as e:
        return error_response(f"创建客户失败: {str(e)}", code=500)


@router.get("/", response_model=dict, summary="获取客户列表")
async def list_customers(
    keyword: Optional[str] = Query(None, description="搜索关键词（客户名称/编码/联系人/电话）"),
    status: Optional[str] = Query(None, description="客户状态筛选（ACTIVE/INACTIVE）"),
    customer_level: Optional[str] = Query(None, description="客户等级筛选（A/B/C/D）"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取客户列表

    支持：
    - 搜索：按客户名称、编码、联系人、电话搜索
    - 筛选：按状态、客户等级筛选
    - 分页：skip/limit参数
    - 排序：客户等级升序，创建时间降序
    """
    try:
        customers = await customer_service.get_customers(
            db=db,
            keyword=keyword,
            status=status,
            customer_level=customer_level,
            skip=skip,
            limit=limit
        )

        customers_list = [
            CustomerListItem.model_validate(customer).model_dump()
            for customer in customers
        ]

        return success_response(data=customers_list)
    except Exception as e:
        return error_response(f"获取客户列表失败: {str(e)}", code=500)


@router.get("/{customer_id}", response_model=dict, summary="获取客户详情")
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """获取客户详细信息"""
    try:
        customer = await customer_service.get_customer(db, customer_id)

        if not customer:
            return error_response(f"客户ID {customer_id} 不存在", code=404)

        return success_response(
            data=CustomerResponse.model_validate(customer).model_dump()
        )
    except Exception as e:
        return error_response(f"获取客户详情失败: {str(e)}", code=500)


@router.put("/{customer_id}", response_model=dict, summary="更新客户信息")
async def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    更新客户信息

    - 客户名称更新时会进行唯一性校验
    - 仅更新提供的字段
    """
    try:
        customer = await customer_service.update_customer(db, customer_id, customer_in)
        return success_response(
            data=CustomerResponse.model_validate(customer).model_dump(),
            msg="客户信息更新成功"
        )
    except ValueError as e:
        return error_response(str(e), code=400)
    except Exception as e:
        return error_response(f"更新客户失败: {str(e)}", code=500)


@router.delete("/{customer_id}", response_model=dict, summary="删除客户")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    删除客户

    - 有关联订单的客户无法删除
    - 建议使用停用状态代替删除
    """
    try:
        await customer_service.delete_customer(db, customer_id)
        return success_response(msg="客户已删除")
    except ValueError as e:
        return error_response(str(e), code=400)
    except Exception as e:
        return error_response(f"删除客户失败: {str(e)}", code=500)


@router.get("/{customer_id}/statistics", response_model=dict, summary="获取客户统计信息")
async def get_customer_statistics(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取客户统计信息

    包括：
    - 总订单数
    - 总交易额
    - 已完成订单数
    - 平均订单金额
    - 最近订单日期
    """
    try:
        # 先检查客户是否存在
        customer = await customer_service.get_customer(db, customer_id)
        if not customer:
            return error_response(f"客户ID {customer_id} 不存在", code=404)

        statistics = await customer_service.get_customer_statistics(db, customer_id)
        return success_response(data=statistics.model_dump())
    except Exception as e:
        return error_response(f"获取客户统计失败: {str(e)}", code=500)


@router.get("/{customer_id}/orders", response_model=dict, summary="获取客户历史订单")
async def get_customer_orders(
    customer_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取客户的历史订单列表

    - 按创建时间降序排列
    - 支持分页
    """
    try:
        # 先检查客户是否存在
        customer = await customer_service.get_customer(db, customer_id)
        if not customer:
            return error_response(f"客户ID {customer_id} 不存在", code=404)

        orders = await customer_service.get_customer_orders(db, customer_id, skip, limit)

        orders_list = [
            OrderListResponse.model_validate(order).model_dump()
            for order in orders
        ]

        return success_response(data=orders_list)
    except Exception as e:
        return error_response(f"获取客户订单失败: {str(e)}", code=500)
