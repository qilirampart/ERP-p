"""
报价计算路由 - 智能开纸与自动报价
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.material import Material
from app.schemas.quote import QuoteCalculateRequest, QuoteCalculateResponse
from app.schemas.response import success_response, error_response
from app.services.calculation_service import CalculationService

router = APIRouter()


@router.post("/calculate", response_model=dict, summary="计算报价")
async def calculate_quote(
    request: QuoteCalculateRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    智能开纸计算 + 自动报价

    核心功能：
    1. 计算最优开纸方案（直切 vs 横切）
    2. 计算纸张消耗数量
    3. 自动生成报价明细
    """
    # 查询纸张信息
    result = await db.execute(
        select(Material).where(Material.id == request.paper_id)
    )
    paper = result.scalar_one_or_none()

    if not paper:
        return error_response(f"纸张ID {request.paper_id} 不存在", code=404)

    if paper.category.value != "PAPER":
        return error_response("选择的物料不是纸张类型", code=400)

    if not paper.spec_width or not paper.spec_length:
        return error_response("纸张规格信息不完整", code=400)

    # 1. 计算开纸方案
    cut_result = CalculationService.calculate_max_cut(
        paper_w=paper.spec_width,
        paper_h=paper.spec_length,
        target_w=request.target_w,
        target_h=request.target_h,
        trim_margin=request.trim_margin
    )

    if cut_result["count"] == 0:
        return error_response("成品尺寸超出纸张规格，无法开纸", code=400)

    # 2. 计算报价
    quote_result = CalculationService.calculate_quote(
        quantity=request.quantity,
        page_count=request.page_count,
        paper_cost_per_sheet=paper.cost_price,
        cut_result=cut_result,
        craft_costs=request.craft_costs
    )

    # 3. 组装响应
    response_data = {
        "cut_method": cut_result["method"],
        "cut_count": cut_result["count"],
        "utilization": cut_result["utilization"],
        "paper_usage": quote_result["paper_usage"],
        "paper_cost": quote_result["paper_cost"],
        "print_cost": quote_result["print_cost"],
        "craft_cost": quote_result["craft_cost"],
        "total_cost": quote_result["total_cost"],
        "paper_name": paper.name,
        "paper_spec": f"{paper.spec_width}×{paper.spec_length}mm {paper.gram_weight}g"
    }

    return success_response(data=response_data, msg="报价计算成功")
