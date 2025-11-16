from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ---------------------- USER SCHEMAS --------------------------

class UserBase(BaseModel):
    name: str
    email: str
    role: str = "customer"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---------------------- ITEM SCHEMAS --------------------------

class ItemBase(BaseModel):
    name: str
    description: str
    price: float
    category: str

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


# ---------------------- INVENTORY SCHEMAS --------------------------

class InventoryBase(BaseModel):
    item_id: int
    stock: int
    unit: str

class InventoryUpdate(BaseModel):
    stock: int

class InventoryResponse(InventoryBase):
    id: int

    class Config:
        orm_mode = True


# ---------------------- ORDER SCHEMAS --------------------------

class OrderItemBase(BaseModel):
    item_id: int
    qty: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemBase]

class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: float
    created_at: datetime

    class Config:
        orm_mode = True


class OrderItemResponse(BaseModel):
    item_id: int
    qty: int
    unit_price: float

    class Config:
        orm_mode = True


class FullOrderResponse(BaseModel):
    id: int
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True
