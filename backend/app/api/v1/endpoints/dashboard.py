"""
仪表盘API端点
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import dashboard_service

router = APIRouter()


@router.get("/stats", summary="获取仪表盘统计数据")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    获取仪表盘统计数据

    包含：
    - 订单统计（今日、总数）
    - 生产统计（生产中、待生产、今日完成）
    - 库存统计（预警数量）
    - 财务统计（本月收款、回款率、应收账款）
    - 最近订单列表
    """
    dashboard_data = await dashboard_service.get_dashboard_stats(db)

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "stats": dashboard_data.stats.model_dump(),
            "recent_orders": [order.model_dump() for order in dashboard_data.recent_orders]
        }
    }
