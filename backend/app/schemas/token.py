"""
认证相关Schema - JWT Token
"""
from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT Token响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenPayload(BaseModel):
    """Token负载"""
    sub: int = Field(..., description="用户ID")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
