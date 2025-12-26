"""
财务报表API端点
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.report import (
    DailyPaymentReport,
    MonthlyPaymentReport,
    CustomerReceivableSummary,
    SalesPaymentTrend,
    ReceivablesAgingAnalysis,
    FinancialOverview
)
from app.services import report_service


router = APIRouter()


@router.get("/payments/daily", summary="收款日报")
async def get_daily_payment_report(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    获取收款日报
    - 按日期范围查询
    - 返回每日收款汇总
    - 包含各收款方式明细
    """
    reports = await report_service.get_daily_payment_report(db, start_date, end_date)

    return {
        "code": 200,
        "msg": "success",
        "data": [report.model_dump() for report in reports]
    }


@router.get("/payments/monthly", summary="收款月报")
async def get_monthly_payment_report(
    year: int = Query(..., description="年份", ge=2000, le=2100),
    month: int = Query(..., description="月份", ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    获取收款月报
    - 指定年月查询
    - 返回当月收款汇总
    - 包含环比增长率
    """
    report = await report_service.get_monthly_payment_report(db, year, month)

    return {
        "code": 200,
        "msg": "success",
        "data": report.model_dump()
    }


@router.get("/receivables/customers", summary="客户欠款统计")
async def get_customer_receivables(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    获取客户欠款统计
    - 返回所有客户的欠款信息
    - 按欠款金额倒序排列
    - 包含总应收、已收、未收汇总
    """
    summary = await report_service.get_customer_receivables(db)

    return {
        "code": 200,
        "msg": "success",
        "data": summary.model_dump()
    }


@router.get("/trends/sales-payment", summary="销售收款趋势")
async def get_sales_payment_trend(
    days: int = Query(30, description="天数", ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    获取销售收款趋势
    - 指定天数范围（默认30天）
    - 返回每日订单和收款数据
    - 用于图表展示
    """
    trend = await report_service.get_sales_payment_trend(db, days)

    return {
        "code": 200,
        "msg": "success",
        "data": trend.model_dump()
    }


@router.get("/receivables/aging", summary="应收账款账龄分析")
async def get_receivables_aging_analysis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    获取应收账款账龄分析
    - 按账龄区间统计（0-7天、8-30天、31-60天、61-90天、90天+）
    - 返回各区间金额和订单数
    - 计算占比百分比
    """
    analysis = await report_service.get_receivables_aging_analysis(db)

    return {
        "code": 200,
        "msg": "success",
        "data": analysis.model_dump()
    }


@router.get("/overview", summary="财务概览")
async def get_financial_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    获取综合财务概览
    - 订单统计（总数、总额、完成数）
    - 收款统计（总笔数、总额、回款率）
    - 应收款统计（总应收、逾期金额）
    - 本月统计
    """
    overview = await report_service.get_financial_overview(db)

    return {
        "code": 200,
        "msg": "success",
        "data": overview.model_dump()
    }
