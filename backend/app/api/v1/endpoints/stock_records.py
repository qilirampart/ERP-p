"""
库存流水记录路由 - 查询库存变动历史
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.stock_record import StockRecord, StockOperationType
from app.models.material import Material
from app.models.user import User
from app.schemas.stock_record import StockRecordResponse, StockRecordWithMaterial
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/", response_model=dict, summary="查询库存流水记录")
async def get_stock_records(
    material_id: Optional[int] = Query(None, description="物料ID"),
    operation_type: Optional[StockOperationType] = Query(None, description="操作类型"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    查询库存流水记录

    支持筛选条件：
    - material_id: 按物料筛选
    - operation_type: 按操作类型筛选 (IN/OUT/ADJUST/RETURN/SCRAP)
    - start_date, end_date: 按日期范围筛选

    分页参数：
    - page: 页码（从1开始）
    - page_size: 每页数量（最大100）
    """
    try:
        # 构建查询
        query = select(StockRecord).options(
            selectinload(StockRecord.material)
        )

        # 应用筛选条件
        conditions = []
        if material_id:
            conditions.append(StockRecord.material_id == material_id)
        if operation_type:
            conditions.append(StockRecord.operation_type == operation_type)
        if start_date:
            conditions.append(StockRecord.created_at >= start_date)
        if end_date:
            conditions.append(StockRecord.created_at < end_date)

        if conditions:
            query = query.where(and_(*conditions))

        # 按时间倒序
        query = query.order_by(desc(StockRecord.created_at))

        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # 执行查询
        result = await db.execute(query)
        records = result.scalars().all()

        # 转换为响应格式（包含物料信息）
        records_data = []
        for record in records:
            record_dict = StockRecordResponse.model_validate(record).model_dump()
            record_dict['material_code'] = record.material.code
            record_dict['material_name'] = record.material.name

            # 查询操作人姓名（如果有）
            if record.operator_id:
                operator_result = await db.execute(
                    select(User).where(User.id == record.operator_id)
                )
                operator = operator_result.scalar_one_or_none()
                if operator:
                    record_dict['operator_name'] = operator.username

            records_data.append(record_dict)

        # 查询总数（用于分页）
        count_query = select(StockRecord)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return success_response(
            data={
                "records": records_data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                }
            },
            msg="查询成功"
        )
    except Exception as e:
        return error_response(f"查询失败: {str(e)}", code=500)


@router.get("/{material_id}", response_model=dict, summary="查询指定物料的流水记录")
async def get_material_stock_records(
    material_id: int,
    limit: int = Query(50, ge=1, le=200, description="返回记录数"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    查询指定物料的最近流水记录

    Args:
        material_id: 物料ID
        limit: 返回记录数（最大200）
    """
    try:
        # 检查物料是否存在
        material_result = await db.execute(
            select(Material).where(Material.id == material_id)
        )
        material = material_result.scalar_one_or_none()

        if not material:
            return error_response(f"物料ID {material_id} 不存在", code=404)

        # 查询流水记录
        query = select(StockRecord).where(
            StockRecord.material_id == material_id
        ).order_by(desc(StockRecord.created_at)).limit(limit)

        result = await db.execute(query)
        records = result.scalars().all()

        # 转换为响应格式
        records_data = [
            StockRecordResponse.model_validate(record).model_dump()
            for record in records
        ]

        return success_response(
            data={
                "material": {
                    "id": material.id,
                    "code": material.code,
                    "name": material.name,
                    "current_stock": float(material.current_stock),
                    "stock_unit": material.stock_unit
                },
                "records": records_data
            },
            msg=f"查询成功，共{len(records_data)}条记录"
        )
    except Exception as e:
        return error_response(f"查询失败: {str(e)}", code=500)
