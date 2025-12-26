"""
PDF生成工具类
"""
from io import BytesIO
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFGenerator:
    """PDF生成器基类"""

    def __init__(self):
        """初始化PDF生成器"""
        self.buffer = BytesIO()
        self.pagesize = A4
        self.width, self.height = self.pagesize

        # 注册中文字体（使用Windows系统自带字体）
        try:
            # 尝试注册微软雅黑
            pdfmetrics.registerFont(TTFont('msyh', 'C:\\Windows\\Fonts\\msyh.ttc'))
            pdfmetrics.registerFont(TTFont('msyhbd', 'C:\\Windows\\Fonts\\msyhbd.ttc'))
            self.font_name = 'msyh'
            self.font_bold = 'msyhbd'
        except:
            try:
                # 如果微软雅黑不可用，尝试使用宋体
                pdfmetrics.registerFont(TTFont('simsun', 'C:\\Windows\\Fonts\\simsun.ttc'))
                self.font_name = 'simsun'
                self.font_bold = 'simsun'
            except:
                # 都不可用则使用Helvetica（不支持中文，但不会报错）
                self.font_name = 'Helvetica'
                self.font_bold = 'Helvetica-Bold'

        # 创建文档样式
        self.styles = self._create_styles()

    def _create_styles(self):
        """创建文档样式"""
        styles = getSampleStyleSheet()

        # 标题样式
        styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName=self.font_bold,
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#1e293b')
        ))

        # 副标题样式
        styles.add(ParagraphStyle(
            name='ChineseSubTitle',
            fontName=self.font_name,
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor('#475569')
        ))

        # 正文样式
        styles.add(ParagraphStyle(
            name='ChineseBody',
            fontName=self.font_name,
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6,
            leading=14
        ))

        # 信息行样式
        styles.add(ParagraphStyle(
            name='ChineseInfo',
            fontName=self.font_name,
            fontSize=9,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#64748b')
        ))

        return styles

    def format_money(self, amount: Decimal) -> str:
        """格式化金额"""
        return f"¥{amount:,.2f}"

    def format_date(self, date) -> str:
        """格式化日期"""
        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d %H:%M")
        return str(date) if date else ""

    def create_header_table(self, data: Dict[str, str]) -> Table:
        """创建信息表格"""
        table_data = []
        for key, value in data.items():
            table_data.append([key, value])

        # 如果是偶数行，两列排布
        if len(table_data) % 2 == 0:
            formatted_data = []
            for i in range(0, len(table_data), 2):
                row = table_data[i] + table_data[i + 1] if i + 1 < len(table_data) else table_data[i]
                formatted_data.append(row)
            col_widths = [3*cm, 6*cm, 3*cm, 6*cm]
        else:
            formatted_data = table_data
            col_widths = [4*cm, 14*cm]

        table = Table(formatted_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#475569')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        return table

    def create_data_table(self, headers: List[str], data: List[List[Any]],
                         col_widths: List[float] = None) -> Table:
        """创建数据表格"""
        # 构建表格数据
        table_data = [headers] + data

        # 创建表格
        table = Table(table_data, colWidths=col_widths)

        # 设置表格样式
        table.setStyle(TableStyle([
            # 表头样式
            ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # 数据行样式
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#475569')),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),

            # 边框
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#cbd5e1')),
        ]))

        return table

    def build_pdf(self, elements: List) -> BytesIO:
        """构建PDF文档"""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer
