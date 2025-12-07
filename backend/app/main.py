"""
Print-ERP 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def create_application() -> FastAPI:
    """创建FastAPI应用实例"""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="印刷行业ERP系统 - 智能开纸计算 & 自动报价",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/")
    async def root() -> dict:
        """根路径健康检查"""
        return {
            "message": "Print-ERP API Server",
            "version": settings.VERSION,
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check() -> dict:
        """健康检查端点"""
        return {"status": "ok"}

    return app


# 创建应用实例
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
