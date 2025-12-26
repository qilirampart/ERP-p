"""
生产工单API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.production import (
    ProductionOrderCreate,
    ProductionOrderUpdate,
    ProductionOrderListItem,
    ProductionOrderDetail,
    ProductionReportCreate,
    ProductionReportResponse,
    ProductionStatistics
)
from app.services import production_service


router = APIRouter()


@router.post("/", summary="创建生产工单")
async def create_production_order(
    data: ProductionOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建生产工单
    - 从已确认订单创建生产工单
    - 自动生成工单号
    - 复制订单明细到生产工单明细
    """
    try:
        production_order = await production_service.create_production_order(db, data)
        return {
            "code": 200,
            "msg": "生产工单创建成功",
            "data": {
                "id": production_order.id,
                "production_no": production_order.production_no,
                "status": production_order.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建生产工单失败: {str(e)}")


@router.get("/", summary="获取生产工单列表")
async def get_production_orders(
    status: Optional[str] = Query(None, description="生产状态筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取生产工单列表
    - 支持按状态筛选
    - 支持分页
    - 按优先级和创建时间排序
    """
    try:
        productions = await production_service.get_production_orders(db, status, skip, limit)
        return {
            "code": 200,
            "msg": "success",
            "data": productions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询生产工单失败: {str(e)}")


@router.get("/{production_id}", summary="获取生产工单详情")
async def get_production_order_detail(
    production_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取生产工单详情
    - 包含生产工单基本信息
    - 包含关联订单信息
    - 包含生产明细列表
    """
    try:
        production_order = await production_service.get_production_order_detail(db, production_id)

        # 组装返回数据
        data = {
            "id": production_order.id,
            "production_no": production_order.production_no,
            "order_id": production_order.order_id,
            "order_no": production_order.order.order_no,
            "customer_name": production_order.order.customer_name,
            "contact_person": production_order.order.contact_person,
            "contact_phone": production_order.order.contact_phone,
            "status": production_order.status.value,
            "priority": production_order.priority,
            "plan_start_date": production_order.plan_start_date,
            "plan_end_date": production_order.plan_end_date,
            "actual_start_date": production_order.actual_start_date,
            "actual_end_date": production_order.actual_end_date,
            "operator_name": production_order.operator_name,
            "machine_name": production_order.machine_name,
            "remark": production_order.remark,
            "created_at": production_order.created_at,
            "updated_at": production_order.updated_at,
            "items": [
                {
                    "id": item.id,
                    "production_order_id": item.production_order_id,
                    "order_item_id": item.order_item_id,
                    "product_name": item.product_name,
                    "plan_quantity": item.plan_quantity,
                    "completed_quantity": item.completed_quantity,
                    "rejected_quantity": item.rejected_quantity,
                    "finished_size_w": item.finished_size_w,
                    "finished_size_h": item.finished_size_h,
                    "page_count": item.page_count,
                    "paper_material_id": item.paper_material_id,
                    "paper_usage": item.paper_usage,
                    "cut_method": item.cut_method,
                    "created_at": item.created_at
                }
                for item in production_order.items
            ]
        }

        return {
            "code": 200,
            "msg": "success",
            "data": data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询生产工单详情失败: {str(e)}")


@router.put("/{production_id}", summary="更新生产工单")
async def update_production_order(
    production_id: int,
    data: ProductionOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新生产工单信息
    - 可更新计划时间、优先级、操作员、设备、备注
    """
    try:
        production_order = await production_service.update_production_order(db, production_id, data)
        return {
            "code": 200,
            "msg": "生产工单更新成功",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新生产工单失败: {str(e)}")


@router.post("/{production_id}/start", summary="开始生产")
async def start_production(
    production_id: int,
    operator_name: str = Query(..., description="操作员姓名"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    开始生产
    - 状态从PENDING变为IN_PROGRESS
    - 记录实际开始时间
    - 创建开工报工记录
    """
    try:
        production_order = await production_service.start_production(db, production_id, operator_name)
        return {
            "code": 200,
            "msg": "生产已开始",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始生产失败: {str(e)}")


@router.post("/{production_id}/complete", summary="完成生产")
async def complete_production(
    production_id: int,
    operator_name: str = Query(..., description="操作员姓名"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    完成生产
    - 状态从IN_PROGRESS变为COMPLETED
    - 记录实际完成时间
    - 创建完工报工记录
    - 如果订单的所有工单都完成，更新订单状态为已完成
    """
    try:
        production_order = await production_service.complete_production(db, production_id, operator_name)
        return {
            "code": 200,
            "msg": "生产已完成",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"完成生产失败: {str(e)}")


@router.post("/{production_id}/cancel", summary="取消生产工单")
async def cancel_production(
    production_id: int,
    reason: str = Query(..., description="取消原因"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消生产工单
    - 只能取消待生产或生产中的工单
    - 已完成的工单不能取消
    - 记录取消原因
    """
    try:
        production_order = await production_service.cancel_production(db, production_id, reason)
        return {
            "code": 200,
            "msg": "生产工单已取消",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消生产工单失败: {str(e)}")


@router.post("/reports/", summary="创建生产报工")
async def create_production_report(
    data: ProductionReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建生产报工记录
    - 报工类型: START/PROGRESS/COMPLETE/REJECT
    - 记录完成数量和报废数量
    """
    try:
        report = await production_service.create_production_report(db, data)
        return {
            "code": 200,
            "msg": "报工成功",
            "data": {
                "id": report.id,
                "report_type": report.report_type,
                "report_time": report.report_time
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报工失败: {str(e)}")


@router.get("/{production_id}/reports/", summary="获取生产报工记录")
async def get_production_reports(
    production_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取生产工单的报工记录列表
    """
    try:
        reports = await production_service.get_production_reports(db, production_id)
        return {
            "code": 200,
            "msg": "success",
            "data": [
                {
                    "id": report.id,
                    "production_order_id": report.production_order_id,
                    "report_type": report.report_type,
                    "completed_quantity": report.completed_quantity,
                    "rejected_quantity": report.rejected_quantity,
                    "operator_name": report.operator_name,
                    "operator_id": report.operator_id,
                    "remark": report.remark,
                    "report_time": report.report_time,
                    "created_at": report.created_at
                }
                for report in reports
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询报工记录失败: {str(e)}")


@router.get("/statistics/summary", summary="获取生产统计")
async def get_production_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取生产统计数据
    - 生产工单总数
    - 各状态数量
    - 今日完成数
    - 平均完成率
    """
    try:
        stats = await production_service.get_production_statistics(db)
        return {
            "code": 200,
            "msg": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询生产统计失败: {str(e)}")
