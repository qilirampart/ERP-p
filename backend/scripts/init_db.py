"""
数据库初始化脚本
创建初始管理员用户和示例数据
"""
import asyncio
from decimal import Decimal
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.material import Material, MaterialCategory
from app.core.security import get_password_hash


async def init_database():
    """初始化数据库数据"""
    async with AsyncSessionLocal() as session:
        print("🚀 开始初始化数据库...")

        # 1. 创建管理员用户
        print("\n📝 创建用户...")
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)

        sales = User(
            username="sales",
            hashed_password=get_password_hash("sales123"),
            role=UserRole.SALES,
            is_active=True
        )
        session.add(sales)

        operator = User(
            username="operator",
            hashed_password=get_password_hash("operator123"),
            role=UserRole.OPERATOR,
            is_active=True
        )
        session.add(operator)

        print("   ✅ 创建了 3 个用户账号")

        # 2. 创建示例纸张物料
        print("\n📦 创建示例物料...")

        materials = [
            Material(
                code="PAPER-001",
                category=MaterialCategory.PAPER,
                name="双铜纸 157g",
                gram_weight=157,
                spec_length=1092,  # 大度对开
                spec_width=787,
                purchase_unit="令",
                stock_unit="张",
                unit_rate=Decimal("500.00"),
                current_stock=Decimal("5000.00"),
                cost_price=Decimal("0.35")
            ),
            Material(
                code="PAPER-002",
                category=MaterialCategory.PAPER,
                name="双铜纸 200g",
                gram_weight=200,
                spec_length=1092,
                spec_width=787,
                purchase_unit="令",
                stock_unit="张",
                unit_rate=Decimal("500.00"),
                current_stock=Decimal("3000.00"),
                cost_price=Decimal("0.45")
            ),
            Material(
                code="PAPER-003",
                category=MaterialCategory.PAPER,
                name="双铜纸 250g",
                gram_weight=250,
                spec_length=1092,
                spec_width=787,
                purchase_unit="令",
                stock_unit="张",
                unit_rate=Decimal("500.00"),
                current_stock=Decimal("2000.00"),
                cost_price=Decimal("0.55")
            ),
            Material(
                code="PAPER-004",
                category=MaterialCategory.PAPER,
                name="哑粉纸 157g",
                gram_weight=157,
                spec_length=1092,
                spec_width=787,
                purchase_unit="令",
                stock_unit="张",
                unit_rate=Decimal("500.00"),
                current_stock=Decimal("4000.00"),
                cost_price=Decimal("0.38")
            ),
            Material(
                code="PAPER-005",
                category=MaterialCategory.PAPER,
                name="特种纸 300g",
                gram_weight=300,
                spec_length=889,  # 正度对开
                spec_width=1194,
                purchase_unit="令",
                stock_unit="张",
                unit_rate=Decimal("500.00"),
                current_stock=Decimal("1000.00"),
                cost_price=Decimal("1.20")
            ),
            Material(
                code="INK-001",
                category=MaterialCategory.INK,
                name="四色油墨套装",
                purchase_unit="套",
                stock_unit="张",  # 这里用"套"更合理，但为了统一用张
                unit_rate=Decimal("1.00"),
                current_stock=Decimal("50.00"),
                cost_price=Decimal("380.00")
            ),
            Material(
                code="AUX-001",
                category=MaterialCategory.AUX,
                name="哑膜",
                purchase_unit="卷",
                stock_unit="张",
                unit_rate=Decimal("1.00"),
                current_stock=Decimal("20.00"),
                cost_price=Decimal("150.00")
            ),
            Material(
                code="AUX-002",
                category=MaterialCategory.AUX,
                name="亮膜",
                purchase_unit="卷",
                stock_unit="张",
                unit_rate=Decimal("1.00"),
                current_stock=Decimal("15.00"),
                cost_price=Decimal("160.00")
            )
        ]

        for material in materials:
            session.add(material)

        print(f"   ✅ 创建了 {len(materials)} 个物料")

        # 提交所有数据
        await session.commit()
        print("\n✨ 数据库初始化完成！\n")

        # 打印账号信息
        print("=" * 50)
        print("📋 账号信息:")
        print("=" * 50)
        print("管理员账号:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("\n销售账号:")
        print("  用户名: sales")
        print("  密码: sales123")
        print("\n操作员账号:")
        print("  用户名: operator")
        print("  密码: operator123")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(init_database())
