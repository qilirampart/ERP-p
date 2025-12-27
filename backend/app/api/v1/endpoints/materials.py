"""
物料管理路由 - CRUD操作 + Excel导入导出
"""
from typing import List, Optional
from io import BytesIO
from datetime import datetime
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.db.session import get_db
from app.models.material import Material, MaterialCategory
from app.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    MaterialWithStatus,
    StockOperationRequest
)
from app.schemas.response import success_response, error_response
from app.services.inventory_service import InventoryService
from app.utils.excel_handler import ExcelHandler

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


# ==================== 库存预警功能 ====================

@router.get("/warnings/stats", response_model=dict, summary="获取库存预警统计")
async def get_warning_stats(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取库存预警统计数据

    返回：
    - total_warning: 总预警数量
    - critical_count: 严重预警数量（库存 <= 最低库存）
    - warning_count: 一般预警数量（最低库存 < 库存 <= 安全库存）
    """
    try:
        stats = await InventoryService.get_warning_stats(db)
        return success_response(data=stats, msg="统计成功")
    except Exception as e:
        return error_response(f"统计失败: {str(e)}", code=500)


@router.get("/warnings", response_model=dict, summary="获取库存预警物料列表")
async def get_warning_materials(
    warning_level: Optional[str] = Query(None, description="预警级别: CRITICAL/WARNING/ALL"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取库存预警物料列表

    参数：
    - warning_level: 预警级别筛选
      - CRITICAL: 严重预警（库存 <= 最低库存）
      - WARNING: 一般预警（最低库存 < 库存 <= 安全库存）
      - ALL 或不传: 所有预警物料

    返回：
    - 物料列表（包含库存状态）
    """
    try:
        materials = await InventoryService.get_warning_materials(db, warning_level)

        # 转换为带状态的响应格式
        materials_data = []
        for material in materials:
            material_dict = MaterialResponse.model_validate(material).model_dump()
            material_dict['stock_status'] = material.get_stock_status()
            materials_data.append(material_dict)

        return success_response(
            data=materials_data,
            msg=f"查询成功，共{len(materials_data)}条预警记录"
        )
    except Exception as e:
        return error_response(f"查询失败: {str(e)}", code=500)


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


# ==================== Excel导入导出功能 ====================

@router.get("/excel/template", summary="下载物料导入模板")
async def download_material_template() -> StreamingResponse:
    """
    下载Excel导入模板

    模板包含：
    - 物料编码（必填）
    - 物料名称（必填）
    - 物料分类（纸张/油墨/其他）
    - 规格
    - 单位
    - 单价
    - 最小库存量
    - 备注
    """
    try:
        # 定义列结构
        columns = {
            'code': '物料编码*',
            'name': '物料名称*',
            'category': '物料分类*(纸张/油墨/其他)',
            'specification': '规格',
            'unit': '单位',
            'unit_price': '单价',
            'min_stock': '最小库存量',
            'remark': '备注'
        }

        # 示例数据
        sample_data = [
            {
                'code': 'MAT001',
                'name': '铜版纸157g',
                'category': '纸张',
                'specification': '787*1092mm',
                'unit': '令',
                'unit_price': 180.00,
                'min_stock': 100,
                'remark': '常用纸张'
            },
            {
                'code': 'MAT002',
                'name': '进口油墨',
                'category': '油墨',
                'specification': '1kg/桶',
                'unit': '桶',
                'unit_price': 450.00,
                'min_stock': 20,
                'remark': '高端印刷用'
            }
        ]

        # 生成模板
        excel_file = ExcelHandler.create_template(
            columns=columns,
            sheet_name='物料导入模板',
            title='物料数据导入模板',
            sample_data=sample_data
        )

        filename = f"物料导入模板_{datetime.now().strftime('%Y%m%d')}.xlsx"
        encoded_filename = quote(filename)

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成模板失败: {str(e)}")


@router.get("/excel/export", summary="导出物料数据到Excel")
async def export_materials_to_excel(
    category: Optional[str] = Query(None, description="物料分类筛选"),
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    导出物料数据到Excel

    支持：
    - 按分类筛选导出
    - 包含库存信息
    - 自动格式化数据
    """
    try:
        # 获取物料数据
        query = select(Material)
        if category:
            query = query.where(Material.category == category)

        query = query.limit(10000)  # 导出最多10000条
        result = await db.execute(query)
        materials = result.scalars().all()

        # 转换为字典列表并格式化
        material_data = []
        for material in materials:
            material_dict = MaterialResponse.model_validate(material).model_dump()

            # 转换分类枚举为中文标签
            category_map = {
                'PAPER': '纸张',
                'INK': '油墨',
                'AUX': '辅料'
            }
            if isinstance(material_dict['category'], str):
                # 处理 "MaterialCategory.PAPER" 格式
                category_value = material_dict['category'].split('.')[-1] if '.' in material_dict['category'] else material_dict['category']
                material_dict['category'] = category_map.get(category_value, category_value)

            # 格式化规格字段（纸张显示完整规格）
            if material.category == MaterialCategory.PAPER and material.spec_width and material.spec_length:
                material_dict['specification'] = f"{material.spec_width}×{material.spec_length}mm {material.gram_weight}g"
            else:
                material_dict['specification'] = '-'

            # 映射字段名到实际存在的字段
            material_dict['unit'] = material_dict.get('stock_unit', '张')
            material_dict['unit_price'] = material_dict.get('cost_price', 0)
            material_dict['stock_quantity'] = material_dict.get('current_stock', 0)

            material_data.append(material_dict)

        # 定义导出列
        columns = {
            'code': '物料编码',
            'name': '物料名称',
            'category': '物料分类',
            'specification': '规格',
            'unit': '单位',
            'unit_price': '单价',
            'stock_quantity': '库存数量',
            'created_at': '创建时间'
        }

        # 生成Excel
        excel_file = ExcelHandler.export_to_excel(
            data=material_data,
            columns=columns,
            sheet_name='物料数据',
            title='物料信息列表'
        )

        filename = f"物料数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        encoded_filename = quote(filename)

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.post("/excel/import", response_model=dict, summary="从Excel批量导入物料")
async def import_materials_from_excel(
    file: UploadFile = File(..., description="Excel文件"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    从Excel文件批量导入物料数据

    要求：
    - 使用标准模板（可通过 /excel/template 下载）
    - 物料编码和名称必填
    - 支持数据验证
    - 返回导入结果统计

    注意：
    - 重复的物料编码将被跳过
    - 无效数据将被记录在错误列表中
    """
    try:
        # 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            return error_response("仅支持Excel文件（.xlsx, .xls）", code=400)

        # 读取文件内容
        content = await file.read()
        file_stream = BytesIO(content)

        # 定义列映射
        columns = {
            'code': '物料编码*',
            'name': '物料名称*',
            'category': '物料分类*(纸张/油墨/其他)',
            'specification': '规格',
            'unit': '单位',
            'unit_price': '单价',
            'min_stock': '最小库存量',
            'remark': '备注'
        }

        # 解析Excel
        try:
            imported_data = ExcelHandler.import_from_excel(
                file=file_stream,
                columns=columns,
                start_row=2
            )
        except ValueError as e:
            return error_response(f"Excel格式错误: {str(e)}", code=400)

        if not imported_data:
            return error_response("Excel文件为空或格式不正确", code=400)

        # 数据验证
        def validate_category(value):
            """验证物料分类"""
            if not value:
                return False  # 必填字段
            return str(value).strip() in ['纸张', '油墨', '其他']

        def validate_price(value):
            """验证价格"""
            if value is None:
                return True  # 可选字段
            try:
                price = float(value)
                return price >= 0
            except:
                return False

        def validate_quantity(value):
            """验证库存数量"""
            if value is None:
                return True  # 可选字段
            try:
                qty = float(value)
                return qty >= 0
            except:
                return False

        validators = {
            'category': validate_category,
            'unit_price': validate_price,
            'min_stock': validate_quantity
        }

        is_valid, validation_errors = ExcelHandler.validate_data(
            data=imported_data,
            required_fields=['code', 'name', 'category'],
            validators=validators
        )

        if not is_valid:
            return error_response(
                msg="数据验证失败",
                code=400,
                data={"errors": validation_errors[:10]}
            )

        # 批量创建物料
        success_count = 0
        error_count = 0
        error_details = []

        for idx, row_data in enumerate(imported_data, 1):
            try:
                # 清理和转换数据
                material_dict = {
                    'code': row_data.get('code', '').strip(),
                    'name': row_data.get('name', '').strip(),
                    'category': row_data.get('category', '').strip(),
                    'specification': row_data.get('specification', '').strip() or None,
                    'unit': row_data.get('unit', '').strip() or '个',
                    'remark': row_data.get('remark', '').strip() or None
                }

                # 处理数值字段
                if row_data.get('unit_price'):
                    material_dict['unit_price'] = Decimal(str(row_data.get('unit_price')))

                if row_data.get('min_stock'):
                    material_dict['min_stock'] = Decimal(str(row_data.get('min_stock')))

                # 检查编码是否重复
                result = await db.execute(
                    select(Material).where(Material.code == material_dict['code'])
                )
                existing = result.scalar_one_or_none()

                if existing:
                    error_count += 1
                    error_details.append({
                        'row': idx,
                        'code': material_dict['code'],
                        'error': f"物料编码已存在"
                    })
                    continue

                # 创建Pydantic模型
                material_in = MaterialCreate(**material_dict)

                # 保存到数据库
                material = Material(**material_in.model_dump())
                db.add(material)
                await db.commit()
                await db.refresh(material)

                success_count += 1

            except ValueError as e:
                error_count += 1
                error_details.append({
                    'row': idx,
                    'code': row_data.get('code', ''),
                    'error': str(e)
                })
            except Exception as e:
                error_count += 1
                error_details.append({
                    'row': idx,
                    'code': row_data.get('code', ''),
                    'error': f"导入失败: {str(e)}"
                })

        # 返回导入结果
        result = {
            'total': len(imported_data),
            'success': success_count,
            'failed': error_count,
            'errors': error_details[:20]
        }

        if error_count > 0:
            return success_response(
                data=result,
                msg=f"导入完成：成功{success_count}条，失败{error_count}条"
            )
        else:
            return success_response(
                data=result,
                msg=f"导入成功：共{success_count}条物料数据"
            )

    except Exception as e:
        return error_response(f"导入失败: {str(e)}", code=500)


