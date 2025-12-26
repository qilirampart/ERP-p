"""
财务报表Schema定义
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date as DateType, datetime
from decimal import Decimal
from typing import List, Dict, Optional


# ==================== 收款日报/月报 ====================

class DailyPaymentReport(BaseModel):
    """收款日报"""
    model_config = ConfigDict(from_attributes=True)

    date: DateType = Field(..., description="日期")
    payment_count: int = Field(..., description="收款笔数")
    total_amount: Decimal = Field(..., description="收款总额")
    cash_amount: Decimal = Field(default=Decimal("0.00"), description="现金金额")
    bank_transfer_amount: Decimal = Field(default=Decimal("0.00"), description="银行转账金额")
    alipay_amount: Decimal = Field(default=Decimal("0.00"), description="支付宝金额")
    wechat_amount: Decimal = Field(default=Decimal("0.00"), description="微信金额")
    check_amount: Decimal = Field(default=Decimal("0.00"), description="支票金额")
    other_amount: Decimal = Field(default=Decimal("0.00"), description="其他方式金额")


class MonthlyPaymentReport(BaseModel):
    """收款月报"""
    model_config = ConfigDict(from_attributes=True)

    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    payment_count: int = Field(..., description="收款笔数")
    total_amount: Decimal = Field(..., description="收款总额")
    average_amount: Decimal = Field(..., description="平均收款金额")
    growth_rate: Optional[Decimal] = Field(None, description="环比增长率（%）")
    payment_methods: Dict[str, Decimal] = Field(default_factory=dict, description="各收款方式统计")


# ==================== 客户欠款统计 ====================

class CustomerReceivable(BaseModel):
    """客户欠款信息"""
    model_config = ConfigDict(from_attributes=True)

    customer_id: int = Field(..., description="客户ID")
    customer_name: str = Field(..., description="客户名称")
    total_order_amount: Decimal = Field(..., description="订单总额")
    paid_amount: Decimal = Field(..., description="已收款金额")
    unpaid_amount: Decimal = Field(..., description="未收款金额（欠款）")
    order_count: int = Field(..., description="订单数量")
    unpaid_order_count: int = Field(..., description="欠款订单数")
    earliest_unpaid_date: Optional[datetime] = Field(None, description="最早欠款日期")


class CustomerReceivableSummary(BaseModel):
    """客户欠款汇总"""
    model_config = ConfigDict(from_attributes=True)

    total_receivable: Decimal = Field(..., description="总应收金额")
    total_paid: Decimal = Field(..., description="总已收金额")
    total_unpaid: Decimal = Field(..., description="总欠款金额")
    customer_count: int = Field(..., description="客户数量")
    unpaid_customer_count: int = Field(..., description="有欠款的客户数")
    customers: List[CustomerReceivable] = Field(default_factory=list, description="客户欠款列表")


# ==================== 销售收款趋势 ====================

class DailyTrend(BaseModel):
    """每日趋势数据"""
    model_config = ConfigDict(from_attributes=True)

    date: DateType = Field(..., description="日期")
    order_amount: Decimal = Field(..., description="订单金额")
    payment_amount: Decimal = Field(..., description="收款金额")
    order_count: int = Field(..., description="订单数量")
    payment_count: int = Field(..., description="收款笔数")


class SalesPaymentTrend(BaseModel):
    """销售收款趋势"""
    model_config = ConfigDict(from_attributes=True)

    start_date: DateType = Field(..., description="开始日期")
    end_date: DateType = Field(..., description="结束日期")
    total_order_amount: Decimal = Field(..., description="总订单金额")
    total_payment_amount: Decimal = Field(..., description="总收款金额")
    total_order_count: int = Field(..., description="总订单数")
    total_payment_count: int = Field(..., description="总收款笔数")
    daily_data: List[DailyTrend] = Field(default_factory=list, description="每日数据")


# ==================== 应收账款账龄分析 ====================

class AgingBracket(BaseModel):
    """账龄区间"""
    model_config = ConfigDict(from_attributes=True)

    bracket_name: str = Field(..., description="账龄区间名称")
    days_range: str = Field(..., description="天数范围")
    amount: Decimal = Field(..., description="金额")
    order_count: int = Field(..., description="订单数量")
    percentage: Decimal = Field(..., description="占比（%）")


class ReceivablesAgingAnalysis(BaseModel):
    """应收账款账龄分析"""
    model_config = ConfigDict(from_attributes=True)

    total_receivable: Decimal = Field(..., description="总应收金额")
    aging_brackets: List[AgingBracket] = Field(default_factory=list, description="账龄区间列表")

    # 快速访问各区间
    bracket_0_7: AgingBracket = Field(..., description="0-7天")
    bracket_8_30: AgingBracket = Field(..., description="8-30天")
    bracket_31_60: AgingBracket = Field(..., description="31-60天")
    bracket_61_90: AgingBracket = Field(..., description="61-90天")
    bracket_90_plus: AgingBracket = Field(..., description="90天以上")


# ==================== 综合财务报表 ====================

class FinancialOverview(BaseModel):
    """财务概览"""
    model_config = ConfigDict(from_attributes=True)

    # 订单统计
    total_orders: int = Field(..., description="总订单数")
    total_order_amount: Decimal = Field(..., description="总订单金额")
    completed_orders: int = Field(..., description="已完成订单数")

    # 收款统计
    total_payments: int = Field(..., description="总收款笔数")
    total_payment_amount: Decimal = Field(..., description="总收款金额")
    payment_rate: Decimal = Field(..., description="回款率（%）")

    # 应收款统计
    total_receivable: Decimal = Field(..., description="总应收金额")
    overdue_amount: Decimal = Field(..., description="逾期金额（30天以上）")
    overdue_count: int = Field(..., description="逾期订单数")

    # 本月统计
    month_order_amount: Decimal = Field(..., description="本月订单金额")
    month_payment_amount: Decimal = Field(..., description="本月收款金额")
    month_order_count: int = Field(..., description="本月订单数")
    month_payment_count: int = Field(..., description="本月收款笔数")
