"""
API v1 路由注册中心
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, materials, quotes, orders, production, customers,
    payments, reports, dashboard, pdf_print, stock_records, print as print_router, users
)

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(materials.router, prefix="/materials", tags=["物料管理"])
api_router.include_router(stock_records.router, prefix="/stock-records", tags=["库存流水"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["报价计算"])
api_router.include_router(orders.router, prefix="/orders", tags=["订单管理"])
api_router.include_router(production.router, prefix="/production", tags=["生产排程"])
api_router.include_router(customers.router, prefix="/customers", tags=["客户管理"])
api_router.include_router(payments.router, prefix="/payments", tags=["收款管理"])
api_router.include_router(reports.router, prefix="/reports", tags=["财务报表"])
api_router.include_router(print_router.router, prefix="/print", tags=["打印"])
api_router.include_router(pdf_print.router, prefix="/pdf", tags=["PDF打印"])



