"""
通用响应Schema
所有API返回统一的包装格式
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel


T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应格式

    Example:
        {
            "code": 200,
            "msg": "success",
            "data": { ... }
        }
    """
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None


def success_response(data: any = None, msg: str = "success") -> dict:
    """成功响应快捷函数"""
    return {"code": 200, "msg": msg, "data": data}


def error_response(msg: str, code: int = 400) -> dict:
    """错误响应快捷函数"""
    return {"code": code, "msg": msg, "data": None}
