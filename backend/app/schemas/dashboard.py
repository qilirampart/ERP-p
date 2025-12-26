"""
仪表盘统计Schema
"""
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class DashboardStats(BaseModel):
    """仪表盘总体统计"""
    model_config = ConfigDict(from_attributes=True)

    # 订单统计
    today_orders_count: int = Field(..., description="今日订单数")
    today_orders_amount: Decimal = Field(..., description="今日订单金额")
    total_orders_count: int = Field(..., description="总订单数")

    # 生产统计
    production_in_progress: int = Field(..., description="生产中工单数")
    production_pending: int = Field(..., description="待生产工单数")
    production_completed_today: int = Field(..., description="今日完成工单数")

    # 库存统计
    low_stock_count: int = Field(..., description="库存预警数量")
    total_materials_count: int = Field(..., description="物料总数")

    # 财务统计
    month_payment_amount: Decimal = Field(..., description="本月收款金额")
    month_order_amount: Decimal = Field(..., description="本月订单金额")
    payment_rate: Decimal = Field(..., description="回款率（%）")
    total_receivable: Decimal = Field(..., description="总应收账款")


class RecentOrder(BaseModel):
    """最近订单"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str = Field(..., description="订单编号")
    customer_name: str = Field(..., description="客户名称")
    total_amount: Decimal = Field(..., description="订单金额")
    status: str = Field(..., description="订单状态")
    created_at: datetime = Field(..., description="创建时间")


class DashboardData(BaseModel):
    """仪表盘完整数据"""
    model_config = ConfigDict(from_attributes=True)

    stats: DashboardStats = Field(..., description="统计数据")
    recent_orders: List[RecentOrder] = Field(..., description="最近订单")
