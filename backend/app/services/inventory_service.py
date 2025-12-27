"""
库存管理服务：库存单位换算与扣减
核心功能：处理不同单位（令/吨/张）的库存变动
"""
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from app.models.material import Material
from app.models.stock_record import StockRecord, StockOperationType


class InventoryService:
    """库存单位换算服务"""

    @staticmethod
    def convert_to_stock_unit(
        quantity: Decimal,
        source_unit: str,
        unit_rate: Decimal
    ) -> Decimal:
        """
        将任意单位转换为库存单位（张）

        Args:
            quantity: 数量
            source_unit: 源单位（如：令、吨）
            unit_rate: 换算率（如：1令=500张，则rate=500）

        Returns:
            库存单位数量（张）
        """
        if source_unit == "张":
            return quantity
        else:
            # 采购单位转库存单位：数量 × 换算率
            return quantity * unit_rate

    @staticmethod
    def convert_from_stock_unit(
        stock_quantity: Decimal,
        target_unit: str,
        unit_rate: Decimal
    ) -> Decimal:
        """
        将库存单位（张）转换为其他单位

        Args:
            stock_quantity: 库存数量（张）
            target_unit: 目标单位（如：令）
            unit_rate: 换算率

        Returns:
            目标单位数量
        """
        if target_unit == "张":
            return stock_quantity
        else:
            # 库存单位转采购单位：数量 ÷ 换算率
            return stock_quantity / unit_rate

    @staticmethod
    async def _create_stock_record(
        db: AsyncSession,
        material_id: int,
        operation_type: StockOperationType,
        quantity: Decimal,
        unit: str,
        before_stock: Decimal,
        after_stock: Decimal,
        order_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        remark: Optional[str] = None
    ) -> StockRecord:
        """
        创建库存流水记录（内部方法）

        Args:
            db: 数据库会话
            material_id: 物料ID
            operation_type: 操作类型
            quantity: 变动数量
            unit: 操作单位
            before_stock: 操作前库存
            after_stock: 操作后库存
            order_id: 关联订单ID
            operator_id: 操作人ID
            remark: 备注

        Returns:
            库存流水记录对象
        """
        record = StockRecord(
            material_id=material_id,
            operation_type=operation_type,
            quantity=quantity,
            unit=unit,
            before_stock=before_stock,
            after_stock=after_stock,
            order_id=order_id,
            operator_id=operator_id,
            remark=remark,
            created_at=datetime.utcnow()
        )
        db.add(record)
        return record

    @staticmethod
    async def stock_in(
        db: AsyncSession,
        material_id: int,
        quantity: Decimal,
        unit: str,
        order_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        remark: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        入库操作（增加库存）

        Args:
            db: 数据库会话
            material_id: 物料ID
            quantity: 入库数量
            unit: 入库单位
            order_id: 关联订单ID
            operator_id: 操作人ID
            remark: 备注

        Returns:
            操作结果字典
        """
        # 查询物料
        result = await db.execute(
            select(Material).where(Material.id == material_id)
        )
        material = result.scalar_one_or_none()

        if not material:
            raise ValueError(f"物料ID {material_id} 不存在")

        # 记录操作前库存
        before_stock = material.current_stock

        # 转换为库存单位
        stock_change = InventoryService.convert_to_stock_unit(
            quantity, unit, material.unit_rate
        )

        # 更新库存
        new_stock = material.current_stock + stock_change
        await db.execute(
            update(Material)
            .where(Material.id == material_id)
            .values(current_stock=new_stock)
        )

        # 创建库存流水记录
        await InventoryService._create_stock_record(
            db=db,
            material_id=material_id,
            operation_type=StockOperationType.IN,
            quantity=quantity,
            unit=unit,
            before_stock=before_stock,
            after_stock=new_stock,
            order_id=order_id,
            operator_id=operator_id,
            remark=remark
        )

        await db.commit()

        return {
            "material_code": material.code,
            "material_name": material.name,
            "quantity": quantity,
            "unit": unit,
            "stock_change": float(stock_change),
            "before_stock": float(before_stock),
            "new_stock": float(new_stock),
            "stock_unit": material.stock_unit
        }

    @staticmethod
    async def stock_out(
        db: AsyncSession,
        material_id: int,
        quantity: Decimal,
        unit: str = "张",
        order_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        remark: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        出库操作（减少库存）

        Args:
            db: 数据库会话
            material_id: 物料ID
            quantity: 出库数量
            unit: 出库单位（通常为"张"）
            order_id: 关联订单ID
            operator_id: 操作人ID
            remark: 备注

        Returns:
            操作结果字典

        Raises:
            ValueError: 库存不足时抛出异常
        """
        # 查询物料
        result = await db.execute(
            select(Material).where(Material.id == material_id)
        )
        material = result.scalar_one_or_none()

        if not material:
            raise ValueError(f"物料ID {material_id} 不存在")

        # 记录操作前库存
        before_stock = material.current_stock

        # 转换为库存单位
        stock_change = InventoryService.convert_to_stock_unit(
            quantity, unit, material.unit_rate
        )

        # 检查库存是否足够
        if material.current_stock < stock_change:
            raise ValueError(
                f"库存不足：当前库存 {material.current_stock} {material.stock_unit}，"
                f"需要 {stock_change} {material.stock_unit}"
            )

        # 更新库存
        new_stock = material.current_stock - stock_change
        await db.execute(
            update(Material)
            .where(Material.id == material_id)
            .values(current_stock=new_stock)
        )

        # 创建库存流水记录
        await InventoryService._create_stock_record(
            db=db,
            material_id=material_id,
            operation_type=StockOperationType.OUT,
            quantity=quantity,
            unit=unit,
            before_stock=before_stock,
            after_stock=new_stock,
            order_id=order_id,
            operator_id=operator_id,
            remark=remark
        )

        await db.commit()

        return {
            "material_code": material.code,
            "material_name": material.name,
            "quantity": quantity,
            "unit": unit,
            "stock_change": float(stock_change),
            "before_stock": float(before_stock),
            "new_stock": float(new_stock),
            "stock_unit": material.stock_unit
        }

    @staticmethod
    async def get_stock_info(
        db: AsyncSession,
        material_id: int,
        display_unit: str = None
    ) -> Dict[str, Any]:
        """
        查询库存信息（支持单位换算显示）

        Args:
            db: 数据库会话
            material_id: 物料ID
            display_unit: 显示单位（None则使用库存单位）

        Returns:
            库存信息字典
        """
        result = await db.execute(
            select(Material).where(Material.id == material_id)
        )
        material = result.scalar_one_or_none()

        if not material:
            raise ValueError(f"物料ID {material_id} 不存在")

        # 如果指定显示单位，则进行换算
        if display_unit and display_unit != material.stock_unit:
            display_quantity = InventoryService.convert_from_stock_unit(
                material.current_stock, display_unit, material.unit_rate
            )
        else:
            display_quantity = material.current_stock
            display_unit = material.stock_unit

        return {
            "material_code": material.code,
            "material_name": material.name,
            "stock_quantity": float(material.current_stock),
            "stock_unit": material.stock_unit,
            "display_quantity": float(display_quantity),
            "display_unit": display_unit,
            "purchase_unit": material.purchase_unit,
            "unit_rate": float(material.unit_rate)
        }

    @staticmethod
    async def get_warning_materials(
        db: AsyncSession,
        warning_level: Optional[str] = None
    ) -> List[Material]:
        """
        获取库存预警物料列表

        Args:
            db: 数据库会话
            warning_level: 预警级别过滤 (CRITICAL/WARNING/ALL)

        Returns:
            预警物料列表
        """
        query = select(Material)

        if warning_level == "CRITICAL":
            # 严重预警：库存 <= 最低库存
            query = query.where(Material.current_stock <= Material.min_stock)
        elif warning_level == "WARNING":
            # 一般预警：最低库存 < 库存 <= 安全库存
            query = query.where(
                and_(
                    Material.current_stock > Material.min_stock,
                    Material.current_stock <= Material.safety_stock
                )
            )
        else:
            # 所有预警：库存 <= 安全库存
            query = query.where(Material.current_stock <= Material.safety_stock)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_warning_stats(db: AsyncSession) -> Dict[str, int]:
        """
        获取库存预警统计

        Args:
            db: 数据库会话

        Returns:
            预警统计字典
        """
        # 查询所有物料
        result = await db.execute(select(Material))
        materials = result.scalars().all()

        critical_count = 0
        warning_count = 0

        for material in materials:
            if material.current_stock <= material.min_stock:
                critical_count += 1
            elif material.current_stock <= material.safety_stock:
                warning_count += 1

        return {
            "total_warning": critical_count + warning_count,
            "critical_count": critical_count,
            "warning_count": warning_count
        }
