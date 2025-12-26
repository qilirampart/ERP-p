"""
生产工单Pydantic Schemas - 用于API请求和响应
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


# ========== 生产工单明细 Schemas ==========

class ProductionOrderItemBase(BaseModel):
    """生产工单明细基础Schema"""
    product_name: str = Field(..., description="产品名称")
    plan_quantity: int = Field(..., gt=0, description="计划生产数量")
    finished_size_w: int = Field(..., gt=0, description="成品宽度mm")
    finished_size_h: int = Field(..., gt=0, description="成品高度mm")
    page_count: int = Field(..., gt=0, description="页数P数")
    paper_material_id: int = Field(..., description="纸张物料ID")


class ProductionOrderItemResponse(ProductionOrderItemBase):
    """生产工单明细响应Schema"""
    id: int
    production_order_id: int
    order_item_id: int
    completed_quantity: int = Field(description="已完成数量")
    rejected_quantity: int = Field(description="报废数量")
    paper_usage: int = Field(description="纸张消耗数量")
    cut_method: str = Field(description="开纸方案 DIRECT/ROTATED")
    created_at: datetime

    model_config = {"from_attributes": True}


# ========== 生产工单 Schemas ==========

class ProductionOrderCreate(BaseModel):
    """创建生产工单请求"""
    order_id: int = Field(..., description="关联订单ID")
    plan_start_date: Optional[datetime] = Field(None, description="计划开始时间")
    plan_end_date: Optional[datetime] = Field(None, description="计划完成时间")
    priority: int = Field(5, ge=1, le=10, description="优先级 1-10，数字越小优先级越高")
    operator_name: Optional[str] = Field(None, description="操作员姓名")
    machine_name: Optional[str] = Field(None, description="设备名称")
    remark: Optional[str] = Field(None, description="备注")


class ProductionOrderUpdate(BaseModel):
    """更新生产工单请求"""
    plan_start_date: Optional[datetime] = Field(None, description="计划开始时间")
    plan_end_date: Optional[datetime] = Field(None, description="计划完成时间")
    priority: Optional[int] = Field(None, ge=1, le=10, description="优先级")
    operator_name: Optional[str] = Field(None, description="操作员姓名")
    machine_name: Optional[str] = Field(None, description="设备名称")
    remark: Optional[str] = Field(None, description="备注")


class ProductionOrderListItem(BaseModel):
    """生产工单列表项"""
    id: int
    production_no: str
    order_id: int
    order_no: str = Field(description="关联订单编号")
    customer_name: str = Field(description="客户名称")
    status: str
    priority: int
    plan_start_date: Optional[datetime]
    plan_end_date: Optional[datetime]
    operator_name: Optional[str]
    machine_name: Optional[str]
    created_at: datetime
    total_plan_quantity: int = Field(description="计划总数量")
    total_completed_quantity: int = Field(description="已完成总数量")
    progress_percent: float = Field(description="完成进度百分比")

    model_config = {"from_attributes": True}


class ProductionOrderDetail(BaseModel):
    """生产工单详情"""
    id: int
    production_no: str
    order_id: int
    order_no: str = Field(description="关联订单编号")
    customer_name: str = Field(description="客户名称")
    contact_person: Optional[str]
    contact_phone: Optional[str]
    status: str
    priority: int
    plan_start_date: Optional[datetime]
    plan_end_date: Optional[datetime]
    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    operator_name: Optional[str]
    machine_name: Optional[str]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: list[ProductionOrderItemResponse]

    model_config = {"from_attributes": True}


# ========== 生产报工 Schemas ==========

class ProductionReportCreate(BaseModel):
    """创建生产报工请求"""
    production_order_id: int = Field(..., description="生产工单ID")
    report_type: str = Field(..., description="报工类型: START/PROGRESS/COMPLETE/REJECT")
    completed_quantity: int = Field(0, ge=0, description="本次完成数量")
    rejected_quantity: int = Field(0, ge=0, description="本次报废数量")
    operator_name: str = Field(..., description="操作员姓名")
    remark: Optional[str] = Field(None, description="报工说明")


class ProductionReportResponse(BaseModel):
    """生产报工响应"""
    id: int
    production_order_id: int
    report_type: str
    completed_quantity: int
    rejected_quantity: int
    operator_name: str
    operator_id: Optional[int]
    remark: Optional[str]
    report_time: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ========== 生产统计 Schemas ==========

class ProductionStatistics(BaseModel):
    """生产统计数据"""
    total_production_orders: int = Field(description="生产工单总数")
    pending_count: int = Field(description="待生产数量")
    in_progress_count: int = Field(description="生产中数量")
    completed_count: int = Field(description="已完成数量")
    today_completed_count: int = Field(description="今日完成数量")
    avg_completion_rate: float = Field(description="平均完成率")
