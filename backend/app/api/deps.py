"""
API依赖注入
提供公共依赖如数据库会话、当前用户等
"""
from typing import AsyncGenerator, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

# OAuth2密码流（Token从Header的Authorization: Bearer <token>获取）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    依赖注入：从JWT Token中获取当前用户ID

    Args:
        token: Bearer Token

    Returns:
        用户ID

    Raises:
        HTTPException: Token无效时抛出401错误
    """
    user_id = decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(user_id)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> User:
    """
    依赖注入：获取当前用户完整对象

    Args:
        db: 数据库会话
        user_id: 当前用户ID

    Returns:
        User对象

    Raises:
        HTTPException: 用户不存在或未激活时抛出错误
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


def require_role(allowed_roles: List[UserRole]):
    """
    权限装饰器工厂：检查用户角色权限

    用法:
        @router.delete("/orders/{order_id}")
        async def delete_order(
            order_id: int,
            current_user: User = Depends(require_role([UserRole.ADMIN]))
        ):
            pass

    Args:
        allowed_roles: 允许访问的角色列表

    Returns:
        依赖函数
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足。需要以下角色之一: {[role.value for role in allowed_roles]}"
            )
        return current_user

    return role_checker
