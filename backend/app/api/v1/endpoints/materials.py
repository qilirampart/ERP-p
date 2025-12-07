"""
物料管理路由 - CRUD操作
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.db.session import get_db
from app.models.material import Material
from app.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    StockOperationRequest
)
from app.schemas.response import success_response, error_response
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.post("/", response_model=dict, summary="创建物料")
async def create_material(
    material_in: MaterialCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """创建新物料"""
    # 检查编码是否重复
    result = await db.execute(
        select(Material).where(Material.code == material_in.code)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return error_response(f"物料编码 '{material_in.code}' 已存在", code=400)

    # 创建物料
    material = Material(**material_in.model_dump())
    db.add(material)
    await db.commit()
    await db.refresh(material)

    return success_response(
        data=MaterialResponse.model_validate(material).model_dump(),
        msg="物料创建成功"
    )


@router.get("/", response_model=dict, summary="获取物料列表")
async def list_materials(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """获取物料列表（支持分页和分类筛选）"""
    query = select(Material)

    if category:
        query = query.where(Material.category == category)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    materials = result.scalars().all()

    return success_response(
        data=[MaterialResponse.model_validate(m).model_dump() for m in materials]
    )


@router.get("/{material_id}", response_model=dict, summary="获取物料详情")
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """获取指定物料详情"""
    result = await db.execute(
        select(Material).where(Material.id == material_id)
    )
    material = result.scalar_one_or_none()

    if not material:
        return error_response(f"物料ID {material_id} 不存在", code=404)

    return success_response(
        data=MaterialResponse.model_validate(material).model_dump()
    )


@router.put("/{material_id}", response_model=dict, summary="更新物料")
async def update_material(
    material_id: int,
    material_in: MaterialUpdate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """更新物料信息"""
    result = await db.execute(
        select(Material).where(Material.id == material_id)
    )
    material = result.scalar_one_or_none()

    if not material:
        return error_response(f"物料ID {material_id} 不存在", code=404)

    # 更新字段
    update_data = material_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)

    await db.commit()
    await db.refresh(material)

    return success_response(
        data=MaterialResponse.model_validate(material).model_dump(),
        msg="物料更新成功"
    )


@router.post("/stock-in", response_model=dict, summary="入库操作")
async def stock_in(
    request: StockOperationRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    物料入库

    - **material_id**: 物料ID
    - **quantity**: 入库数量
    - **unit**: 入库单位（如：令、吨）
    """
    try:
        result = await InventoryService.stock_in(
            db, request.material_id, request.quantity, request.unit
        )
        return success_response(data=result, msg="入库成功")
    except ValueError as e:
        return error_response(str(e), code=400)


@router.post("/stock-out", response_model=dict, summary="出库操作")
async def stock_out(
    request: StockOperationRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    物料出库

    - **material_id**: 物料ID
    - **quantity**: 出库数量
    - **unit**: 出库单位（通常为'张'）
    """
    try:
        result = await InventoryService.stock_out(
            db, request.material_id, request.quantity, request.unit
        )
        return success_response(data=result, msg="出库成功")
    except ValueError as e:
        return error_response(str(e), code=400)
