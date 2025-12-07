"""
API依赖注入
提供公共依赖如数据库会话、当前用户等
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_access_token

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
):
    """
    依赖注入：获取当前用户完整对象

    注意：需要在创建User模型后实现查询逻辑

    Args:
        db: 数据库会话
        user_id: 当前用户ID

    Returns:
        User对象

    Raises:
        HTTPException: 用户不存在时抛出404错误
    """
    # TODO: 在创建User模型后实现
    # from app.models.user import User
    # from sqlalchemy import select
    #
    # result = await db.execute(select(User).where(User.id == user_id))
    # user = result.scalar_one_or_none()
    #
    # if not user:
    #     raise HTTPException(status_code=404, detail="用户不存在")
    #
    # return user

    # 临时返回（避免未使用变量警告）
    return {"id": user_id, "username": "placeholder"}
