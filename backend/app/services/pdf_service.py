"""
PDF打印服务
"""
from io import BytesIO
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.units import cm

from app.utils.pdf_generator import PDFGenerator
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.production import ProductionOrder, ProductionOrderItem, ProductionReport
from app.models.payment import OrderPayment
from app.models.customer import Customer
from app.models.material import Material


class PrintService:
    """打印服务类"""

    @staticmethod
    async def generate_order_pdf(db: AsyncSession, order_id: int) -> BytesIO:
        """
        生成销售订单PDF

        Args:
            db: 数据库会话
            order_id: 订单ID

        Returns:
            PDF文件的BytesIO对象
        """
        # 查询订单信息
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            raise ValueError(f"订单不存在: {order_id}")

        # 创建PDF生成器
        generator = PDFGenerator()
        elements = []

        # 标题
        title = Paragraph("销售订单", generator.styles['ChineseTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))

        # 订单基本信息
        order_info = {
            "订单编号:": order.order_no,
            "客户名称:": order.customer_name or "未知",
            "联系人:": order.contact_person or "未填写",
            "联系电话:": order.contact_phone or "未填写",
            "订单日期:": generator.format_date(order.created_at),
            "订单状态:": {
                'DRAFT': '草稿',
                'CONFIRMED': '已确认',
                'PRODUCTION': '生产中',
                'COMPLETED': '已完成'
            }.get(order.status, order.status),
        }

        info_table = generator.create_header_table(order_info)
        elements.append(info_table)
        elements.append(Spacer(1, 0.8*cm))

        # 产品明细表
        detail_subtitle = Paragraph("产品明细", generator.styles['ChineseSubTitle'])
        elements.append(detail_subtitle)
        elements.append(Spacer(1, 0.3*cm))

        # 表头
        headers = ['序号', '产品名称', '规格', '数量', '单价', '金额']

        # 表格数据
        table_data = []
        for idx, item in enumerate(order.items or [], 1):
            specifications = f"{item.finished_size_w}x{item.finished_size_h}mm"
            table_data.append([
                str(idx),
                item.product_name,
                specifications,
                str(item.quantity),
                generator.format_money(item.item_amount / item.quantity if item.quantity > 0 else 0),
                generator.format_money(item.item_amount)
            ])

        # 列宽
        col_widths = [1.5*cm, 5*cm, 4*cm, 2*cm, 2.5*cm, 2.5*cm]
        detail_table = generator.create_data_table(headers, table_data, col_widths)
        elements.append(detail_table)
        elements.append(Spacer(1, 0.5*cm))

        # 合计信息
        summary_data = [
            ['', '', '', '', '订单金额:', generator.format_money(order.total_amount)],
        ]
        summary_table = generator.create_data_table([], summary_data, col_widths)
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*cm))

        # 备注
        if order.remark:
            notes = Paragraph(f"<b>备注:</b> {order.remark}", generator.styles['ChineseBody'])
            elements.append(notes)

        # 生成PDF
        return generator.build_pdf(elements)

    @staticmethod
    async def generate_production_pdf(db: AsyncSession, production_id: int) -> BytesIO:
        """
        生成生产工单PDF

        Args:
            db: 数据库会话
            production_id: 生产工单ID

        Returns:
            PDF文件的BytesIO对象
        """
        # 查询生产工单信息，包括关联的items和order
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
            raise ValueError(f"生产工单不存在: {production_id}")

        # 创建PDF生成器
        generator = PDFGenerator()
        elements = []

        # 标题
        title = Paragraph("生产工单", generator.styles['ChineseTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))

        # 工单基本信息
        production_info = {
            "工单编号:": production.production_no,
            "关联订单:": production.order.order_no if production.order else "无",
            "客户名称:": production.order.customer_name if production.order else "无",
            "优先级:": f"P{production.priority}",
            "计划开始:": generator.format_date(production.plan_start_date),
            "计划完成:": generator.format_date(production.plan_end_date),
            "工单状态:": {
                'PENDING': '待生产',
                'IN_PROGRESS': '生产中',
                'COMPLETED': '已完成',
                'CANCELLED': '已取消'
            }.get(production.status, production.status),
        }

        if production.operator_name:
            production_info["操作员:"] = production.operator_name
        if production.machine_name:
            production_info["设备:"] = production.machine_name

        info_table = generator.create_header_table(production_info)
        elements.append(info_table)
        elements.append(Spacer(1, 0.8*cm))

        # 生产明细表
        if production.items:
            items_subtitle = Paragraph("生产明细", generator.styles['ChineseSubTitle'])
            elements.append(items_subtitle)
            elements.append(Spacer(1, 0.3*cm))

            headers = ['序号', '产品名称', '规格尺寸', '计划数量', '已完成', '报废数', '纸张用量']
            table_data = []

            for idx, item in enumerate(production.items, 1):
                specifications = f"{item.finished_size_w}x{item.finished_size_h}mm"
                table_data.append([
                    str(idx),
                    item.product_name,
                    specifications,
                    str(item.plan_quantity),
                    str(item.completed_quantity),
                    str(item.rejected_quantity),
                    f"{item.paper_usage}张"
                ])

            col_widths = [1.5*cm, 4*cm, 3*cm, 2*cm, 2*cm, 2*cm, 2.5*cm]
            items_table = generator.create_data_table(headers, table_data, col_widths)
            elements.append(items_table)
            elements.append(Spacer(1, 0.5*cm))

        # 实际执行情况（如果已开始）
        if production.actual_start_date:
            actual_subtitle = Paragraph("执行记录", generator.styles['ChineseSubTitle'])
            elements.append(actual_subtitle)
            elements.append(Spacer(1, 0.3*cm))

            # 计算总完成数量
            total_completed = sum(item.completed_quantity for item in production.items)
            total_rejected = sum(item.rejected_quantity for item in production.items)

            actual_info = {
                "实际开始:": generator.format_date(production.actual_start_date),
                "实际完成:": generator.format_date(production.actual_end_date) if production.actual_end_date else "进行中",
                "完成数量:": str(total_completed),
                "报废数量:": str(total_rejected),
            }

            actual_table = generator.create_header_table(actual_info)
            elements.append(actual_table)

        # 备注
        if production.remark:
            elements.append(Spacer(1, 0.5*cm))
            notes = Paragraph(f"<b>备注:</b> {production.remark}", generator.styles['ChineseBody'])
            elements.append(notes)

        # 生成PDF
        return generator.build_pdf(elements)

    @staticmethod
    async def generate_delivery_pdf(db: AsyncSession, order_id: int) -> BytesIO:
        """
        生成送货单PDF

        Args:
            db: 数据库会话
            order_id: 订单ID

        Returns:
            PDF文件的BytesIO对象
        """
        # 查询订单信息
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            raise ValueError(f"订单不存在: {order_id}")

        # 创建PDF生成器
        generator = PDFGenerator()
        elements = []

        # 标题
        title = Paragraph("送货单", generator.styles['ChineseTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))

        # 送货基本信息
        delivery_info = {
            "送货单号:": f"SH{order.order_no[2:]}",
            "订单编号:": order.order_no,
            "客户名称:": order.customer_name or "未知",
            "联系人:": order.contact_person or "未填写",
            "联系电话:": order.contact_phone or "未填写",
            "送货日期:": generator.format_date(datetime.now()),
        }

        info_table = generator.create_header_table(delivery_info)
        elements.append(info_table)
        elements.append(Spacer(1, 0.8*cm))

        # 货物明细表
        detail_subtitle = Paragraph("货物明细", generator.styles['ChineseSubTitle'])
        elements.append(detail_subtitle)
        elements.append(Spacer(1, 0.3*cm))

        # 表头
        headers = ['序号', '产品名称', '规格', '数量', '单位']

        # 表格数据
        table_data = []
        for idx, item in enumerate(order.items or [], 1):
            specifications = f"{item.finished_size_w}x{item.finished_size_h}mm"
            table_data.append([
                str(idx),
                item.product_name,
                specifications,
                str(item.quantity),
                '件'
            ])

        # 列宽
        col_widths = [2*cm, 6*cm, 5*cm, 2*cm, 2*cm]
        detail_table = generator.create_data_table(headers, table_data, col_widths)
        elements.append(detail_table)
        elements.append(Spacer(1, 1*cm))

        # 签收栏
        signature_text = Paragraph(
            "收货人签字: _______________    日期: _______________",
            generator.styles['ChineseBody']
        )
        elements.append(signature_text)

        # 生成PDF
        return generator.build_pdf(elements)

    @staticmethod
    async def generate_payment_receipt_pdf(db: AsyncSession, payment_id: int) -> BytesIO:
        """
        生成收款凭证PDF

        Args:
            db: 数据库会话
            payment_id: 收款记录ID

        Returns:
            PDF文件的BytesIO对象
        """
        # 查询收款记录
        stmt = (
            select(OrderPayment)
            .where(OrderPayment.id == payment_id)
            .options(selectinload(OrderPayment.order))
        )
        result = await db.execute(stmt)
        payment = result.scalar_one_or_none()

        if not payment:
            raise ValueError(f"收款记录不存在: {payment_id}")

        # 创建PDF生成器
        generator = PDFGenerator()
        elements = []

        # 标题
        title = Paragraph("收款凭证", generator.styles['ChineseTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))

        # 收款基本信息
        payment_info = {
            "凭证编号:": payment.payment_no,
            "关联订单:": payment.order.order_no if payment.order else "无",
            "客户名称:": payment.order.customer_name if payment.order else "未知",
            "收款日期:": generator.format_date(payment.payment_date),
            "收款方式:": {
                'CASH': '现金',
                'BANK_TRANSFER': '银行转账',
                'ALIPAY': '支付宝',
                'WECHAT': '微信支付',
                'OTHER': '其他'
            }.get(payment.payment_method, payment.payment_method),
            "收款状态:": {
                'PENDING': '待确认',
                'CONFIRMED': '已确认',
                'CANCELLED': '已取消'
            }.get(payment.status, payment.status),
        }

        info_table = generator.create_header_table(payment_info)
        elements.append(info_table)
        elements.append(Spacer(1, 0.8*cm))

        # 金额信息
        amount_subtitle = Paragraph("收款金额", generator.styles['ChineseSubTitle'])
        elements.append(amount_subtitle)
        elements.append(Spacer(1, 0.3*cm))

        # 金额表格
        amount_headers = ['项目', '金额']
        amount_data = [
            ['本次收款', generator.format_money(payment.payment_amount)],
        ]

        if payment.order:
            amount_data.append(['订单总额', generator.format_money(payment.order.total_amount)])

        col_widths = [8*cm, 8*cm]
        amount_table = generator.create_data_table(amount_headers, amount_data, col_widths)
        elements.append(amount_table)

        # 备注
        if payment.remark:
            elements.append(Spacer(1, 0.5*cm))
            notes = Paragraph(f"<b>备注:</b> {payment.remark}", generator.styles['ChineseBody'])
            elements.append(notes)

        # 生成PDF
        return generator.build_pdf(elements)
