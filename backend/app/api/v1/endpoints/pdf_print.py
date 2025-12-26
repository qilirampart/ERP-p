"""
PDF打印API端点
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.pdf_service import PrintService

router = APIRouter()


@router.get("/order/{order_id}", summary="下载销售订单PDF")
async def download_order_pdf(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载销售订单PDF

    Args:
        order_id: 订单ID

    Returns:
        PDF文件流
    """
    try:
        pdf_buffer = await PrintService.generate_order_pdf(db, order_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=order_{order_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")


@router.get("/production/{production_id}", summary="下载生产工单PDF")
async def download_production_pdf(
    production_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载生产工单PDF

    Args:
        production_id: 生产工单ID

    Returns:
        PDF文件流
    """
    try:
        pdf_buffer = await PrintService.generate_production_pdf(db, production_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=production_{production_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")


@router.get("/delivery/{order_id}", summary="下载送货单PDF")
async def download_delivery_pdf(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载送货单PDF

    Args:
        order_id: 订单ID

    Returns:
        PDF文件流
    """
    try:
        pdf_buffer = await PrintService.generate_delivery_pdf(db, order_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=delivery_{order_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")


@router.get("/payment/{payment_id}", summary="下载收款凭证PDF")
async def download_payment_receipt_pdf(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载收款凭证PDF

    Args:
        payment_id: 收款记录ID

    Returns:
        PDF文件流
    """
    try:
        pdf_buffer = await PrintService.generate_payment_receipt_pdf(db, payment_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=payment_{payment_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成PDF失败: {str(e)}")
