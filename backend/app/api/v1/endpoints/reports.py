"""
财务报表API端点 + Excel导出
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from typing import List
from io import BytesIO
from urllib.parse import quote

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
from app.utils.excel_handler import ExcelHandler, DataFrameExporter


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


# ==================== Excel导出功能 ====================

@router.get("/excel/daily-payments", summary="导出收款日报")
async def export_daily_payment_report(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    导出收款日报到Excel

    包含：
    - 每日收款汇总
    - 各收款方式明细
    - 统计数据
    """
    try:
        # 获取报表数据
        reports = await report_service.get_daily_payment_report(db, start_date, end_date)

        # 转换为字典列表
        report_data = []
        for report in reports:
            report_dict = report.model_dump()
            # 格式化日期
            if isinstance(report_dict.get('date'), date):
                report_dict['date'] = report_dict['date'].strftime('%Y-%m-%d')
            report_data.append(report_dict)

        # 定义导出列
        columns = {
            'date': '日期',
            'total_amount': '总收款金额',
            'cash': '现金',
            'bank_transfer': '银行转账',
            'alipay': '支付宝',
            'wechat': '微信支付',
            'other': '其他',
            'payment_count': '收款笔数'
        }

        # 生成Excel
        excel_file = ExcelHandler.export_to_excel(
            data=report_data,
            columns=columns,
            sheet_name='收款日报',
            title=f'收款日报 ({start_date} 至 {end_date})'
        )

        filename = f"收款日报_{start_date}至{end_date}.xlsx"
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


@router.get("/excel/customer-receivables", summary="导出客户欠款统计")
async def export_customer_receivables(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    导出客户欠款统计到Excel

    包含：
    - 客户欠款明细
    - 总应收、已收、未收汇总
    """
    try:
        # 获取报表数据
        summary = await report_service.get_customer_receivables(db)

        # 转换为字典列表
        report_data = []
        for customer in summary.customers:
            customer_dict = customer.model_dump()
            report_data.append(customer_dict)

        # 定义导出列
        columns = {
            'customer_name': '客户名称',
            'total_orders': '订单数',
            'total_amount': '订单总额',
            'paid_amount': '已收金额',
            'unpaid_amount': '未收金额',
            'payment_rate': '回款率(%)'
        }

        # 生成Excel (添加汇总数据)
        excel_file = ExcelHandler.export_to_excel(
            data=report_data,
            columns=columns,
            sheet_name='客户欠款统计',
            title='客户欠款统计表'
        )

        filename = f"客户欠款统计_{datetime.now().strftime('%Y%m%d')}.xlsx"
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


@router.get("/excel/receivables-aging", summary="导出应收账款账龄分析")
async def export_receivables_aging(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    导出应收账款账龄分析到Excel

    包含：
    - 各账龄区间统计
    - 金额和订单数
    - 占比百分比
    """
    try:
        # 获取报表数据
        analysis = await report_service.get_receivables_aging_analysis(db)

        # 转换为字典列表
        aging_data = []
        for aging in analysis.aging_distribution:
            aging_dict = aging.model_dump()
            aging_data.append(aging_dict)

        # 定义导出列
        columns = {
            'age_range': '账龄区间',
            'amount': '欠款金额',
            'order_count': '订单数',
            'percentage': '占比(%)'
        }

        # 生成Excel
        excel_file = ExcelHandler.export_to_excel(
            data=aging_data,
            columns=columns,
            sheet_name='账龄分析',
            title='应收账款账龄分析表'
        )

        filename = f"应收账款账龄分析_{datetime.now().strftime('%Y%m%d')}.xlsx"
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


@router.get("/excel/financial-overview", summary="导出财务概览")
async def export_financial_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    导出综合财务概览到Excel

    包含：
    - 订单统计
    - 收款统计
    - 应收款统计
    - 本月统计
    """
    try:
        # 获取报表数据
        overview = await report_service.get_financial_overview(db)
        overview_dict = overview.model_dump()

        # 将概览数据转换为多个Sheet
        import pandas as pd
        from decimal import Decimal

        # 辅助函数：安全地将值转换为float（处理Decimal和字符串）
        def to_float(value):
            if isinstance(value, str):
                return float(value)
            elif isinstance(value, Decimal):
                return float(value)
            return value

        # Sheet 1: 订单统计
        order_data = pd.DataFrame([{
            '指标': '订单总数',
            '数值': overview_dict['total_orders']
        }, {
            '指标': '订单总额',
            '数值': f"{to_float(overview_dict['total_order_amount']):.2f}"
        }, {
            '指标': '已完成订单数',
            '数值': overview_dict['completed_orders']
        }])

        # Sheet 2: 收款统计
        payment_data = pd.DataFrame([{
            '指标': '收款总笔数',
            '数值': overview_dict['total_payments']
        }, {
            '指标': '收款总额',
            '数值': f"{to_float(overview_dict['total_payment_amount']):.2f}"
        }, {
            '指标': '回款率',
            '数值': f"{to_float(overview_dict['payment_rate']):.2f}%"
        }])

        # Sheet 3: 应收款统计
        receivable_data = pd.DataFrame([{
            '指标': '总应收金额',
            '数值': f"{to_float(overview_dict['total_receivable']):.2f}"
        }, {
            '指标': '逾期金额',
            '数值': f"{to_float(overview_dict['overdue_amount']):.2f}"
        }, {
            '指标': '逾期订单数',
            '数值': overview_dict['overdue_count']
        }])

        # Sheet 4: 本月统计
        monthly_data = pd.DataFrame([{
            '指标': '本月新增订单',
            '数值': overview_dict['month_order_count']
        }, {
            '指标': '本月订单金额',
            '数值': f"{to_float(overview_dict['month_order_amount']):.2f}"
        }, {
            '指标': '本月收款金额',
            '数值': f"{to_float(overview_dict['month_payment_amount']):.2f}"
        }, {
            '指标': '本月收款笔数',
            '数值': overview_dict['month_payment_count']
        }])

        # 使用DataFrameExporter导出多个Sheet
        sheets_dict = {
            '订单统计': order_data,
            '收款统计': payment_data,
            '应收款统计': receivable_data,
            '本月统计': monthly_data
        }

        excel_file = DataFrameExporter.export_multi_sheet(sheets_dict)

        filename = f"财务概览_{datetime.now().strftime('%Y%m%d')}.xlsx"
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
