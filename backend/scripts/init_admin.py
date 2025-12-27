"""
初始化超级管理员账号

使用方法:
cd backend
poetry run python scripts/init_admin.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def init_admin():
    """初始化超级管理员账号"""
    async with AsyncSessionLocal() as db:
        # 检查是否已存在admin用户
        result = await db.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("[ERROR] 超级管理员账号已存在！")
            print(f"   用户名: {existing_admin.username}")
            print(f"   角色: {existing_admin.role.value}")
            print(f"   状态: {'激活' if existing_admin.is_active else '禁用'}")
            return

        # 创建超级管理员
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),  # 默认密码
            role=UserRole.ADMIN,
            is_active=True
        )

        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)

        print("[SUCCESS] 超级管理员账号创建成功！")
        print(f"   用户名: admin")
        print(f"   密码: admin123")
        print(f"   角色: {admin_user.role.value}")
        print(f"\n[WARNING] 请在首次登录后立即修改密码！")


if __name__ == "__main__":
    print("=" * 50)
    print("初始化超级管理员账号")
    print("=" * 50)
    asyncio.run(init_admin())
