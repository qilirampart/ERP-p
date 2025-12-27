"""
打印功能API端点 - 生成各种PDF单据
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import print_service

router = APIRouter()


@router.get("/order/{order_id}", summary="打印销售订单")
async def print_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成销售订单PDF
    """
    try:
        pdf_buffer = await print_service.generate_order_pdf(db, order_id)

        return StreamingResponse(
            BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=order_{order_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")


@router.get("/production/{production_id}", summary="打印生产工单")
async def print_production(
    production_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成生产工单PDF
    """
    try:
        pdf_buffer = await print_service.generate_production_pdf(db, production_id)

        return StreamingResponse(
            BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=production_{production_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")


@router.get("/delivery/{order_id}", summary="打印送货单")
async def print_delivery(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成送货单PDF
    """
    try:
        pdf_buffer = await print_service.generate_delivery_pdf(db, order_id)

        return StreamingResponse(
            BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=delivery_{order_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")


@router.get("/payment/{payment_id}", summary="打印收款凭证")
async def print_payment_receipt(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成收款凭证PDF
    """
    try:
        pdf_buffer = await print_service.generate_payment_receipt_pdf(db, payment_id)

        return StreamingResponse(
            BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=payment_{payment_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")
