from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.auth import require_role


router = APIRouter(
    prefix="/items",
    tags=["Items"]
)


# ------------------------------
# CREATE ITEM (Manager Only)
# ------------------------------
@router.post("/", response_model=schemas.ItemResponse)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):
    # Create the item
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # Create inventory entry for the item
    inv = models.Inventory(
        item_id=db_item.id,
        stock=0,
        unit="pcs"
    )
    db.add(inv)
    db.commit()

    return db_item


# ------------------------------
# GET ALL ITEMS (Public)
# ------------------------------
@router.get("/", response_model=list[schemas.ItemResponse])
def get_items(
    db: Session = Depends(get_db),
):
    items = db.query(models.Item).filter(
        models.Item.is_active == True
    ).all()
    return items


# ------------------------------
# GET SINGLE ITEM
# ------------------------------
@router.get("/{item_id}", response_model=schemas.ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(
        models.Item.id == item_id,
        models.Item.is_active == True
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    return item


# ------------------------------
# UPDATE ITEM (Manager Only)
# ------------------------------
@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(
    item_id: int,
    item_data: schemas.ItemCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not item:
        raise HTTPException(404, "Item not found")

    for key, value in item_data.dict().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


# ------------------------------
# SOFT DELETE ITEM (Manager Only)
# ------------------------------
@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if not item:
        raise HTTPException(404, "Item not found")

    # Soft delete
    item.is_active = False
    db.commit()

    return {"message": f"Item {item_id} deactivated"}


# ------------------------------
# UPDATE INVENTORY (Manager Only)
# ------------------------------
@router.patch("/inventory/{item_id}", response_model=schemas.InventoryResponse)
def update_inventory(
    item_id: int,
    inv_data: schemas.InventoryUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("manager"))
):
    inventory = db.query(models.Inventory).filter(
        models.Inventory.item_id == item_id
    ).first()

    if not inventory:
        raise HTTPException(404, "Inventory not found")

    inventory.stock = inv_data.stock
    db.commit()
    db.refresh(inventory)

    return inventory
