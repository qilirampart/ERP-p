"""
报价计算相关Schema
"""
from decimal import Decimal
from typing import Optional, Dict
from pydantic import BaseModel, Field


class QuoteCalculateRequest(BaseModel):
    """报价计算请求"""
    paper_id: int = Field(..., gt=0, description="纸张物料ID")
    target_w: int = Field(..., gt=0, description="成品宽度 mm")
    target_h: int = Field(..., gt=0, description="成品高度 mm")
    quantity: int = Field(..., gt=0, description="印数")
    page_count: int = Field(default=1, gt=0, description="页数（P数）")
    trim_margin: int = Field(default=0, ge=0, description="修边尺寸 mm")
    craft_costs: Optional[Dict[str, Decimal]] = Field(None, description="工艺费用字典")


class QuoteCalculateResponse(BaseModel):
    """报价计算响应"""
    # 开纸方案
    cut_method: str = Field(..., description="开纸方案 (DIRECT/ROTATED)")
    cut_count: int = Field(..., description="单张大纸开数")
    utilization: float = Field(..., description="纸张利用率 0-1")

    # 纸张消耗
    paper_usage: int = Field(..., description="纸张消耗（张）")

    # 费用明细
    paper_cost: Decimal = Field(..., description="纸张成本")
    print_cost: Decimal = Field(..., description="印刷工费")
    craft_cost: Decimal = Field(..., description="工艺费用")
    total_cost: Decimal = Field(..., description="总成本")

    # 纸张信息
    paper_name: str = Field(..., description="纸张名称")
    paper_spec: str = Field(..., description="纸张规格")
