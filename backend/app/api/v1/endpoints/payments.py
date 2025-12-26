"""
收款管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.payment import (
    OrderPaymentCreate,
    OrderPaymentUpdate,
    OrderPaymentResponse,
    OrderPaymentSummary
)
from app.services import payment_service


router = APIRouter()


@router.post("/", summary="创建收款记录")
async def create_payment(
    data: OrderPaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建收款记录
    - 自动生成收款单号
    - 记录收款信息
    """
    try:
        payment = await payment_service.create_order_payment(db, data)
        return {
            "code": 200,
            "msg": "收款记录创建成功",
            "data": {
                "id": payment.id,
                "payment_no": payment.payment_no,
                "payment_amount": payment.payment_amount
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建收款记录失败: {str(e)}")


@router.get("/", summary="获取收款记录列表")
async def get_payments(
    order_id: Optional[int] = Query(None, description="订单ID筛选"),
    status: Optional[str] = Query(None, description="收款状态筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收款记录列表
    - 支持按订单筛选
    - 支持按状态筛选
    - 支持分页
    """
    try:
        payments = await payment_service.get_order_payments(db, order_id, status, skip, limit)
        return {
            "code": 200,
            "msg": "success",
            "data": payments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询收款记录失败: {str(e)}")


@router.get("/{payment_id}", summary="获取收款记录详情")
async def get_payment_detail(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收款记录详情
    """
    try:
        payment = await payment_service.get_order_payment_detail(db, payment_id)

        data = {
            "id": payment.id,
            "order_id": payment.order_id,
            "order_no": payment.order.order_no,
            "customer_name": payment.order.customer_name,
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
        }

        return {
            "code": 200,
            "msg": "success",
            "data": data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询收款记录详情失败: {str(e)}")


@router.put("/{payment_id}", summary="更新收款记录")
async def update_payment(
    payment_id: int,
    data: OrderPaymentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新收款记录
    - 可更新收款金额、方式、日期、收款人等
    """
    try:
        payment = await payment_service.update_order_payment(db, payment_id, data)
        return {
            "code": 200,
            "msg": "收款记录更新成功",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新收款记录失败: {str(e)}")


@router.post("/{payment_id}/cancel", summary="取消收款记录")
async def cancel_payment(
    payment_id: int,
    reason: str = Query(..., description="取消原因"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消收款记录
    - 记录取消原因
    """
    try:
        payment = await payment_service.cancel_order_payment(db, payment_id, reason)
        return {
            "code": 200,
            "msg": "收款记录已取消",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消收款记录失败: {str(e)}")


@router.get("/orders/{order_id}/summary", summary="获取订单收款汇总")
async def get_order_payment_summary(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取订单收款汇总
    - 订单总金额
    - 已收款金额
    - 未收款金额
    - 收款状态
    """
    try:
        summary = await payment_service.get_order_payment_summary(db, order_id)
        return {
            "code": 200,
            "msg": "success",
            "data": summary.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询订单收款汇总失败: {str(e)}")


@router.get("/statistics/summary", summary="获取收款统计")
async def get_payment_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收款统计数据
    - 总收款记录数
    - 总收款金额
    - 今日收款金额
    - 各收款方式统计
    """
    try:
        stats = await payment_service.get_payment_statistics(db)
        return {
            "code": 200,
            "msg": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询收款统计失败: {str(e)}")
