"""
用户管理Schema
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# ==================== 基础 Schema ====================

class UserBase(BaseModel):
    """用户基础字段"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    role: UserRole = Field(default=UserRole.OPERATOR, description="用户角色")
    is_active: bool = Field(default=True, description="是否激活")


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role: UserRole = Field(default=UserRole.OPERATOR, description="用户角色")
    is_active: bool = Field(default=True, description="是否激活")


class UserUpdate(BaseModel):
    """更新用户请求"""
    password: Optional[str] = Field(None, min_length=6, max_length=50, description="密码（可选）")
    role: Optional[UserRole] = Field(None, description="用户角色")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserChangePassword(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=50, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class UserResponse(BaseModel):
    """用户响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户角色")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class UserListResponse(BaseModel):
    """用户列表响应"""
    users: list[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总数")
