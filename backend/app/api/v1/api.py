"""
API v1 路由注册中心
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, materials, quotes, orders

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(materials.router, prefix="/materials", tags=["物料管理"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["报价计算"])
api_router.include_router(orders.router, prefix="/orders", tags=["订单管理"])

# 后续添加更多路由
# api_router.include_router(production.router, prefix="/production", tags=["生产报工"])
