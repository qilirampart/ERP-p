"""
客户管理路由 - CRUD + 统计分析 + Excel导入导出
"""
from typing import List, Optional
from io import BytesIO
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
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
from app.utils.excel_handler import ExcelHandler

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


# ==================== Excel导入导出功能 ====================

@router.get("/excel/template", summary="下载客户导入模板")
async def download_customer_template() -> StreamingResponse:
    """
    下载Excel导入模板

    模板包含：
    - 客户名称（必填）
    - 联系人
    - 联系电话
    - 联系地址
    - 客户等级（A/B/C/D）
    - 备注
    """
    try:
        # 定义列结构（带*表示必填）
        columns = {
            'name': '客户名称*',
            'contact_person': '联系人',
            'contact_phone': '联系电话',
            'contact_address': '联系地址',
            'customer_level': '客户等级(A/B/C/D)',
            'remark': '备注'
        }

        # 示例数据
        sample_data = [
            {
                'name': '示例客户公司',
                'contact_person': '张三',
                'contact_phone': '13800138000',
                'contact_address': '北京市朝阳区XX路XX号',
                'customer_level': 'A',
                'remark': '重要客户'
            }
        ]

        # 生成模板
        excel_file = ExcelHandler.create_template(
            columns=columns,
            sheet_name='客户导入模板',
            title='客户数据导入模板',
            sample_data=sample_data
        )

        # 生成文件名
        from urllib.parse import quote
        filename = f"客户导入模板_{datetime.now().strftime('%Y%m%d')}.xlsx"
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


@router.get("/excel/export", summary="导出客户数据到Excel")
async def export_customers_to_excel(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="客户状态筛选"),
    customer_level: Optional[str] = Query(None, description="客户等级筛选"),
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    导出客户数据到Excel

    支持：
    - 按条件筛选导出
    - 包含客户统计信息
    - 自动格式化数据
    """
    try:
        # 获取客户数据（不分页，导出所有符合条件的数据）
        customers = await customer_service.get_customers(
            db=db,
            keyword=keyword,
            status=status,
            customer_level=customer_level,
            skip=0,
            limit=10000  # 导出最多10000条
        )

        # 转换为字典列表
        customer_data = []
        for customer in customers:
            customer_dict = CustomerListItem.model_validate(customer).model_dump()
            customer_data.append(customer_dict)

        # 定义导出列
        columns = {
            'customer_no': '客户编号',
            'name': '客户名称',
            'contact_person': '联系人',
            'contact_phone': '联系电话',
            'contact_address': '联系地址',
            'customer_level': '客户等级',
            'status': '状态',
            'total_orders': '订单总数',
            'total_amount': '交易总额',
            'created_at': '创建时间',
            'remark': '备注'
        }

        # 生成Excel
        excel_file = ExcelHandler.export_to_excel(
            data=customer_data,
            columns=columns,
            sheet_name='客户数据',
            title='客户信息列表'
        )

        # 生成文件名
        from urllib.parse import quote
        filename = f"客户数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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


@router.post("/excel/import", response_model=dict, summary="从Excel批量导入客户")
async def import_customers_from_excel(
    file: UploadFile = File(..., description="Excel文件"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    从Excel文件批量导入客户数据

    要求：
    - 使用标准模板（可通过 /excel/template 下载）
    - 客户名称必填
    - 支持数据验证
    - 返回导入结果统计

    注意：
    - 重复的客户名称将被跳过
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
            'name': '客户名称*',
            'contact_person': '联系人',
            'contact_phone': '联系电话',
            'contact_address': '联系地址',
            'customer_level': '客户等级(A/B/C/D)',
            'remark': '备注'
        }

        # 解析Excel
        try:
            imported_data = ExcelHandler.import_from_excel(
                file=file_stream,
                columns=columns,
                start_row=2  # 第1行是标题，第2行是表头
            )
        except ValueError as e:
            return error_response(f"Excel格式错误: {str(e)}", code=400)

        if not imported_data:
            return error_response("Excel文件为空或格式不正确", code=400)

        # 数据验证
        def validate_phone(value):
            """验证电话号码"""
            if not value:
                return True  # 可选字段
            value = str(value).strip()
            return len(value) >= 7  # 简单验证长度

        def validate_level(value):
            """验证客户等级"""
            if not value:
                return True  # 可选字段
            return str(value).upper() in ['A', 'B', 'C', 'D']

        validators = {
            'contact_phone': validate_phone,
            'customer_level': validate_level
        }

        is_valid, validation_errors = ExcelHandler.validate_data(
            data=imported_data,
            required_fields=['name'],
            validators=validators
        )

        if not is_valid:
            return error_response(
                msg="数据验证失败",
                code=400,
                data={"errors": validation_errors[:10]}  # 只返回前10个错误
            )

        # 批量创建客户
        success_count = 0
        error_count = 0
        error_details = []

        for idx, row_data in enumerate(imported_data, 1):
            try:
                # 清理和转换数据
                customer_dict = {
                    'name': row_data.get('name', '').strip(),
                    'contact_person': row_data.get('contact_person', '').strip() or None,
                    'contact_phone': row_data.get('contact_phone', '').strip() or None,
                    'contact_address': row_data.get('contact_address', '').strip() or None,
                    'customer_level': row_data.get('customer_level', 'D').strip().upper(),
                    'remark': row_data.get('remark', '').strip() or None
                }

                # 创建Pydantic模型
                customer_in = CustomerCreate(**customer_dict)

                # 保存到数据库
                await customer_service.create_customer(db, customer_in)
                success_count += 1

            except ValueError as e:
                # 业务逻辑错误（如客户名重复）
                error_count += 1
                error_details.append({
                    'row': idx,
                    'name': row_data.get('name', ''),
                    'error': str(e)
                })
            except Exception as e:
                # 其他错误
                error_count += 1
                error_details.append({
                    'row': idx,
                    'name': row_data.get('name', ''),
                    'error': f"导入失败: {str(e)}"
                })

        # 返回导入结果
        result = {
            'total': len(imported_data),
            'success': success_count,
            'failed': error_count,
            'errors': error_details[:20]  # 最多返回20个错误详情
        }

        if error_count > 0:
            return success_response(
                data=result,
                msg=f"导入完成：成功{success_count}条，失败{error_count}条"
            )
        else:
            return success_response(
                data=result,
                msg=f"导入成功：共{success_count}条客户数据"
            )

    except Exception as e:
        return error_response(f"导入失败: {str(e)}", code=500)
