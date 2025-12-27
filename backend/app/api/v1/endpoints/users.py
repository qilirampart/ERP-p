"""
用户管理API端点
只有管理员才能访问这些接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.db.session import get_db
from app.models.user import User, UserRole
from app.api.deps import get_current_user, require_role
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserChangePassword
)
from app.core.security import get_password_hash, verify_password


router = APIRouter()


@router.get("/", summary="获取用户列表")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
) -> dict:
    """
    获取用户列表（仅管理员）

    - 支持分页
    - 返回所有用户信息
    """
    # 查询总数
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar_one()

    # 查询用户列表
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "users": [UserResponse.model_validate(user) for user in users],
            "total": total
        }
    }


@router.post("/", summary="创建用户")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
) -> dict:
    """
    创建新用户（仅管理员）

    - 检查用户名是否已存在
    - 密码会被加密存储
    """
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 创建新用户
    new_user = User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=user_data.is_active
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "code": 200,
        "msg": "用户创建成功",
        "data": UserResponse.model_validate(new_user)
    }


@router.get("/{user_id}", summary="获取用户详情")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
) -> dict:
    """
    获取用户详情（仅管理员）
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return {
        "code": 200,
        "msg": "success",
        "data": UserResponse.model_validate(user)
    }


@router.put("/{user_id}", summary="更新用户")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
) -> dict:
    """
    更新用户信息（仅管理员）

    - 可以修改角色、密码、激活状态
    - 密码如果提供则会被加密存储
    - 不能修改其他管理员（安全保护）
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止管理员禁用自己
    if user.id == current_user.id and user_data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己的账号"
        )

    # 防止修改其他管理员（安全保护）
    if user.role == UserRole.ADMIN and user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能修改其他管理员的信息，这是系统安全保护"
        )

    # 更新字段
    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return {
        "code": 200,
        "msg": "用户更新成功",
        "data": UserResponse.model_validate(user)
    }


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
) -> dict:
    """
    删除用户（仅管理员）

    - 不能删除自己
    - 不能删除其他管理员（安全保护）
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止管理员删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )

    # 防止删除其他管理员账号（安全保护）
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能删除管理员账号，这是系统安全保护"
        )

    await db.delete(user)
    await db.commit()

    return {
        "code": 200,
        "msg": "用户删除成功"
    }


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: UserChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    修改当前用户密码（所有用户都可以）

    - 需要提供原密码验证
    """
    # 验证原密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )

    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()

    return {
        "code": 200,
        "msg": "密码修改成功"
    }
