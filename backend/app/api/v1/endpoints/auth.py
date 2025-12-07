"""
认证路由 - 登录与Token获取
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token, LoginRequest
from app.schemas.response import success_response, error_response
from app.core.security import verify_password, create_access_token

router = APIRouter()


@router.post("/login", response_model=dict, summary="用户登录")
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    用户登录获取JWT Token

    - **username**: 用户名
    - **password**: 密码
    """
    # 查询用户
    result = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()

    # 验证用户存在且密码正确
    if not user or not verify_password(login_data.password, user.hashed_password):
        return error_response("用户名或密码错误", code=401)

    # 检查用户是否激活
    if not user.is_active:
        return error_response("用户已被禁用", code=403)

    # 生成Token
    access_token = create_access_token(data={"sub": str(user.id)})

    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value
        },
        msg="登录成功"
    )


@router.post("/token", response_model=Token, summary="OAuth2兼容Token端点")
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    OAuth2标准登录端点（用于Swagger UI测试）
    """
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")
