from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from app.database import get_db
from app import models
from app.utils.auth import require_role

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# -----------------------
# 1. DAILY SALES SUMMARY
# -----------------------
@router.get("/daily-sales")
def daily_sales(
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):
    today = date.today()
    
    total_sales = db.query(
        func.sum(models.Order.total_amount)
    ).filter(
        func.date(models.Order.created_at) == today,
        models.Order.status != "cancelled"
    ).scalar() or 0

    orders_count = db.query(models.Order).filter(
        func.date(models.Order.created_at) == today,
        models.Order.status != "cancelled"
    ).count()

    return {
        "date": today,
        "total_sales": float(total_sales),
        "orders_count": orders_count
    }


# -----------------------
# 2. WEEKLY SALES SUMMARY
# -----------------------
@router.get("/weekly-sales")
def weekly_sales(
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):

    start = date.today() - timedelta(days=7)

    total_sales = db.query(
        func.sum(models.Order.total_amount)
    ).filter(
        models.Order.created_at >= start,
        models.Order.status != "cancelled"
    ).scalar() or 0

    return {
        "start_date": start,
        "end_date": date.today(),
        "weekly_sales": float(total_sales)
    }


# -----------------------
# 3. TOP-SELLING ITEMS
# -----------------------
@router.get("/top-items")
def top_items(
    limit: int = 5,
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):

    items = db.query(
        models.Item.name,
        func.sum(models.OrderItem.qty).label("qty_sold")
    ).join(models.OrderItem).join(models.Order).filter(
        models.Order.status != "cancelled"
    ).group_by(models.Item.name).order_by(
        func.sum(models.OrderItem.qty).desc()
    ).limit(limit).all()

    return [{"item": r[0], "qty_sold": int(r[1])} for r in items]


# -----------------------
# 4. LOW STOCK ITEMS
# -----------------------
@router.get("/low-stock")
def low_stock(
    threshold: int = 10,
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):

    items = db.query(
        models.Item.name,
        models.Inventory.stock,
        models.Inventory.unit
    ).join(models.Inventory).filter(
        models.Inventory.stock <= threshold
    ).all()

    return [
        {"item": r[0], "stock": r[1], "unit": r[2]}
        for r in items
    ]


# -----------------------
# 5. DATE RANGE REPORT
# -----------------------
@router.get("/range-sales")
def range_sales(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):

    try:
        s = datetime.strptime(start_date, "%Y-%m-%d")
        e = datetime.strptime(end_date, "%Y-%m-%d")
    except:
        return {"error": "Use format YYYY-MM-DD"}

    total = db.query(
        func.sum(models.Order.total_amount)
    ).filter(
        models.Order.created_at >= s,
        models.Order.created_at <= e,
        models.Order.status != "cancelled"
    ).scalar() or 0

    return {
        "start_date": s,
        "end_date": e,
        "total_sales": float(total)
    }
