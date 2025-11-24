from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.auth import require_role

router = APIRouter(prefix="/orders", tags=["Orders"])

def restore_inventory(order_id: int, db: Session):
    order_items = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == order_id
    ).all()

    for item in order_items:
        inventory = db.query(models.Inventory).filter(
            models.Inventory.item_id == item.item_id
        ).first()

        inventory.stock += item.qty
        db.commit()



# ---- CREATE ORDER ----
@router.post("/", response_model=schemas.FullOrderResponse)
def create_order(order: schemas.OrderCreate, 
                 db: Session = Depends(get_db),
                 user=Depends(require_role("customer", "manager"))):

    new_order = models.Order(user_id=order.user_id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    total = 0

    for item in order.items:
        db_item = db.query(models.Item).filter(models.Item.id == item.item_id).first()
        if not db_item:
            raise HTTPException(404, f"Item {item.item_id} not found")

        inventory = db.query(models.Inventory).filter(
            models.Inventory.item_id == item.item_id
        ).first()

        if inventory.stock < item.qty:
            raise HTTPException(400, f"Not enough stock for item {item.item_id}")

        inventory.stock -= item.qty
        db.commit()

        order_item = models.OrderItem(
            order_id=new_order.id,
            item_id=item.item_id,
            qty=item.qty,
            unit_price=db_item.price,
        )
        db.add(order_item)

        total += db_item.price * item.qty

    new_order.total_amount = total
    db.commit()
    db.refresh(new_order)

    # -------- FIX: build response manually --------
    items_response = []

    for oi in new_order.items:
        items_response.append({
            "item_id": oi.item_id,
            "name": oi.item.name,
            "qty": oi.qty,
            "unit_price": oi.unit_price
        })

    return {
        "id": new_order.id,
        "status": new_order.status,
        "total_amount": new_order.total_amount,
        "created_at": new_order.created_at,
        "items": items_response
    }

                                                               


# ---- GET ORDER ----
@router.get("/{order_id}", response_model=schemas.FullOrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    
    items_response=[]

    for oi in order.items:
        items_response.append({
            "item_id": oi.item_id,
            "name": oi.item.name,         # <-- Get name here
            "qty": oi.qty,
            "unit_price": oi.unit_price
        })

    return {
        "id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
        "created_at": order.created_at,
        "items": items_response
    }


# ---- UPDATE ORDER STATUS ----
@router.patch("/{order_id}/status")
def update_status(order_id: int, status: str,
                  db: Session = Depends(get_db),
                  user=Depends(require_role("staff", "manager"))):

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    valid = ["created", "preparing", "ready", "completed", "cancelled"]
    if status not in valid:
        raise HTTPException(400, "Invalid status")

    # If order is cancelled → restore stock
    if status == "cancelled":
        restore_inventory(order_id, db)

    order.status = status
    db.commit()
    return {"message": f"Order updated to {status}"}
