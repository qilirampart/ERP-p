"""
核心算法：智能开纸计算服务
计算给定纸张尺寸和成品尺寸的最优切割方案
"""
from typing import Dict, Any
from decimal import Decimal
import math


class CutMethod:
    """开纸方案枚举"""
    DIRECT = "DIRECT"      # 直切（不旋转）
    ROTATED = "ROTATED"    # 横切（旋转90度）


class CalculationService:
    """开纸计算与报价服务"""

    @staticmethod
    def calculate_max_cut(
        paper_w: int,
        paper_h: int,
        target_w: int,
        target_h: int,
        trim_margin: int = 0
    ) -> Dict[str, Any]:
        """
        计算最大开纸数量

        Args:
            paper_w: 大纸宽度 (mm)
            paper_h: 大纸高度 (mm)
            target_w: 成品宽度 (mm)
            target_h: 成品高度 (mm)
            trim_margin: 修边尺寸/咬口位 (mm)，默认0

        Returns:
            字典包含:
            - count: 最大开数
            - method: 开纸方案 (DIRECT/ROTATED)
            - utilization: 纸张利用率 (0-1)
            - cut_x: X方向切割数
            - cut_y: Y方向切割数
        """
        # 扣除修边尺寸
        usable_w = paper_w - trim_margin
        usable_h = paper_h - trim_margin

        # 场景A：直切（纹路对应）
        cut_a_x = math.floor(usable_w / target_w)
        cut_a_y = math.floor(usable_h / target_h)
        total_a = cut_a_x * cut_a_y

        # 场景B：横切（旋转90度）
        cut_b_x = math.floor(usable_w / target_h)
        cut_b_y = math.floor(usable_h / target_w)
        total_b = cut_b_x * cut_b_y

        # 选择最优方案
        if total_a >= total_b:
            count = total_a
            method = CutMethod.DIRECT
            cut_x, cut_y = cut_a_x, cut_a_y
        else:
            count = total_b
            method = CutMethod.ROTATED
            cut_x, cut_y = cut_b_x, cut_b_y

        # 计算利用率
        paper_area = paper_w * paper_h
        used_area = count * target_w * target_h
        utilization = used_area / paper_area if paper_area > 0 else 0

        return {
            "count": count,
            "method": method,
            "utilization": round(utilization, 4),
            "cut_x": cut_x,
            "cut_y": cut_y,
            "usable_w": usable_w,
            "usable_h": usable_h
        }

    @staticmethod
    def calculate_paper_usage(
        quantity: int,
        page_count: int,
        cut_count: int
    ) -> int:
        """
        计算纸张消耗数量

        Args:
            quantity: 印数（成品数量）
            page_count: 页数（P数）
            cut_count: 单张大纸开数

        Returns:
            需要的大纸张数
        """
        # 总印张数 = 印数 × 页数 ÷ 2（正反面）
        total_prints = math.ceil(quantity * page_count / 2)

        # 需要的大纸张数 = 总印张数 ÷ 开数
        paper_needed = math.ceil(total_prints / cut_count)

        return paper_needed

    @staticmethod
    def calculate_quote(
        quantity: int,
        page_count: int,
        paper_cost_per_sheet: Decimal,
        cut_result: Dict[str, Any],
        print_cost_per_impression: Decimal = Decimal("0.10"),
        craft_costs: Dict[str, Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        计算报价明细

        Args:
            quantity: 印数
            page_count: 页数
            paper_cost_per_sheet: 纸张单价（元/张）
            cut_result: 开纸计算结果
            print_cost_per_impression: 印刷工费（元/印次）
            craft_costs: 工艺费用字典 {"laminate": 500, "uv": 300}

        Returns:
            费用明细字典:
            - paper_cost: 纸张成本
            - print_cost: 印刷工费
            - craft_cost: 工艺费用
            - total_cost: 总成本
        """
        # 纸张消耗
        paper_usage = CalculationService.calculate_paper_usage(
            quantity, page_count, cut_result["count"]
        )

        # 纸张成本
        paper_cost = Decimal(paper_usage) * paper_cost_per_sheet

        # 印刷工费（按印次计算）
        total_impressions = math.ceil(quantity * page_count / 2)
        print_cost = Decimal(total_impressions) * print_cost_per_impression

        # 工艺费用
        craft_cost = Decimal("0.00")
        if craft_costs:
            craft_cost = sum(Decimal(str(v)) for v in craft_costs.values())

        # 总成本
        total_cost = paper_cost + print_cost + craft_cost

        return {
            "paper_cost": paper_cost.quantize(Decimal("0.01")),
            "print_cost": print_cost.quantize(Decimal("0.01")),
            "craft_cost": craft_cost.quantize(Decimal("0.01")),
            "total_cost": total_cost.quantize(Decimal("0.01")),
            "paper_usage": paper_usage
        }
