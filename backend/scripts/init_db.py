"""
Database initialization script
Create initial admin users and sample data
"""
import asyncio
from decimal import Decimal
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.material import Material, MaterialCategory
from app.core.security import get_password_hash


async def init_database():
    """Initialize database with default data"""
    async with AsyncSessionLocal() as session:
        print("Starting database initialization...")

        # 1. Create admin users
        print("\nCreating users...")
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

        print("   Created 3 user accounts")

        # 2. Create sample materials
        print("\nCreating sample materials...")

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

        print(f"   Created {len(materials)} materials")

        # Commit all data
        await session.commit()
        print("\nDatabase initialization completed!\n")

        # Print account information
        print("=" * 50)
        print("Account Information:")
        print("=" * 50)
        print("Admin Account:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nSales Account:")
        print("  Username: sales")
        print("  Password: sales123")
        print("\nOperator Account:")
        print("  Username: operator")
        print("  Password: operator123")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(init_database())
