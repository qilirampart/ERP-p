"""
打印服务 - 使用ReportLab生成PDF单据
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from io import BytesIO
from datetime import datetime

from app.models.production import ProductionOrder
from app.models.order import Order

# 注册中文字体（使用系统自带的Microsoft YaHei）
try:
    pdfmetrics.registerFont(TTFont('SimHei', 'C:\\Windows\\Fonts\\simhei.ttf'))
    FONT_NAME = 'SimHei'
except:
    # 如果找不到SimHei，使用Helvetica（英文字体）
    FONT_NAME = 'Helvetica'


async def generate_production_pdf(db: AsyncSession, production_id: int) -> bytes:
    """
    生成生产工单PDF
    """
    # 查询生产工单
    stmt = (
        select(ProductionOrder)
        .where(ProductionOrder.id == production_id)
        .options(
            selectinload(ProductionOrder.order),
            selectinload(ProductionOrder.items)
        )
    )

    result = await db.execute(stmt)
    production = result.scalar_one_or_none()

    if not production:
        raise ValueError(f"生产工单ID {production_id} 不存在")

    # 创建PDF buffer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 设置字体
    c.setFont(FONT_NAME, 12)

    # 标题
    c.setFont(FONT_NAME, 20)
    c.drawCentredString(width / 2, height - 40*mm, "生产工单")

    # 基本信息
    y_position = height - 60*mm
    c.setFont(FONT_NAME, 12)

    # 左侧信息
    x_left = 40*mm
    c.drawString(x_left, y_position, f"工单号: {production.production_no}")
    y_position -= 7*mm
    c.drawString(x_left, y_position, f"关联订单: {production.order.order_no}")
    y_position -= 7*mm
    c.drawString(x_left, y_position, f"客户名称: {production.order.customer_name}")
    y_position -= 7*mm
    c.drawString(x_left, y_position, f"联系人: {production.order.contact_person or '-'}")
    y_position -= 7*mm
    c.drawString(x_left, y_position, f"联系电话: {production.order.contact_phone or '-'}")

    # 右侧信息
    y_position = height - 60*mm
    x_right = 120*mm

    status_map = {
        'PENDING': '待生产',
        'IN_PROGRESS': '生产中',
        'COMPLETED': '已完成',
        'CANCELLED': '已取消'
    }
    c.drawString(x_right, y_position, f"状态: {status_map.get(production.status.value, production.status.value)}")
    y_position -= 7*mm
    c.drawString(x_right, y_position, f"优先级: P{production.priority}")
    y_position -= 7*mm
    c.drawString(x_right, y_position, f"操作员: {production.operator_name or '-'}")
    y_position -= 7*mm
    c.drawString(x_right, y_position, f"设备: {production.machine_name or '-'}")
    y_position -= 7*mm

    if production.plan_start_date:
        plan_start = production.plan_start_date.strftime('%Y-%m-%d %H:%M')
        c.drawString(x_right, y_position, f"计划开始: {plan_start}")
    else:
        c.drawString(x_right, y_position, "计划开始: -")

    # 生产明细表格
    y_position -= 15*mm
    c.setFont(FONT_NAME, 14)
    c.drawString(x_left, y_position, "生产明细")

    # 表头
    y_position -= 10*mm
    c.setFont(FONT_NAME, 10)
    table_headers = ["产品名称", "成品尺寸", "页数", "计划数量", "完成数量", "报废数量"]
    x_positions = [x_left, x_left + 50*mm, x_left + 80*mm, x_left + 95*mm, x_left + 115*mm, x_left + 135*mm]

    # 绘制表头
    for i, header in enumerate(table_headers):
        c.drawString(x_positions[i], y_position, header)

    # 表头下划线
    y_position -= 3*mm
    c.line(x_left, y_position, x_left + 150*mm, y_position)

    # 表格内容
    for item in production.items:
        y_position -= 7*mm

        # 检查是否需要新页
        if y_position < 40*mm:
            c.showPage()
            c.setFont(FONT_NAME, 10)
            y_position = height - 40*mm

        size = f"{item.finished_size_w}x{item.finished_size_h}mm"

        c.drawString(x_positions[0], y_position, item.product_name[:15])  # 限制长度
        c.drawString(x_positions[1], y_position, size)
        c.drawString(x_positions[2], y_position, f"{item.page_count}P")
        c.drawString(x_positions[3], y_position, str(item.plan_quantity))
        c.drawString(x_positions[4], y_position, str(item.completed_quantity))
        c.drawString(x_positions[5], y_position, str(item.rejected_quantity))

    # 备注
    if production.remark:
        y_position -= 15*mm
        c.setFont(FONT_NAME, 10)
        c.drawString(x_left, y_position, f"备注: {production.remark}")

    # 页脚
    c.setFont(FONT_NAME, 8)
    c.drawString(x_left, 20*mm, f"打印时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawRightString(width - 40*mm, 20*mm, f"第1页")

    # 保存PDF
    c.save()

    # 返回PDF字节
    buffer.seek(0)
    return buffer.getvalue()


async def generate_order_pdf(db: AsyncSession, order_id: int) -> bytes:
    """
    生成销售订单PDF（简化版本）
    """
    # 查询订单
    stmt = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )

    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError(f"订单ID {order_id} 不存在")

    # 创建PDF buffer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # 标题
    c.setFont(FONT_NAME, 20)
    c.drawCentredString(width / 2, height - 40*mm, "销售订单")

    # 基本信息
    y_position = height - 60*mm
    c.setFont(FONT_NAME, 12)
    x_left = 40*mm

    c.drawString(x_left, y_position, f"订单号: {order.order_no}")
    y_position -= 7*mm
    c.drawString(x_left, y_position, f"客户名称: {order.customer_name}")
    y_position -= 7*mm
    c.drawString(x_left, y_position, f"订单金额: ¥{order.total_amount}")
    y_position -= 7*mm

    status_map = {
        'PENDING': '待确认',
        'CONFIRMED': '已确认',
        'PRODUCTION': '生产中',
        'COMPLETED': '已完成',
        'CANCELLED': '已取消'
    }
    c.drawString(x_left, y_position, f"订单状态: {status_map.get(order.status.value, order.status.value)}")

    # 页脚
    c.setFont(FONT_NAME, 8)
    c.drawString(x_left, 20*mm, f"打印时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


async def generate_delivery_pdf(db: AsyncSession, order_id: int) -> bytes:
    """
    生成送货单PDF（简化版本）
    """
    return await generate_order_pdf(db, order_id)


async def generate_payment_receipt_pdf(db: AsyncSession, payment_id: int) -> bytes:
    """
    生成收款凭证PDF（简化版本）
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont(FONT_NAME, 20)
    c.drawCentredString(width / 2, height - 40*mm, "收款凭证")

    c.setFont(FONT_NAME, 12)
    c.drawString(40*mm, height - 60*mm, f"收款ID: {payment_id}")
    c.drawString(40*mm, height - 70*mm, "功能开发中...")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
