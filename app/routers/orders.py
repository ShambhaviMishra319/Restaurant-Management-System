from fastapi import APIRouter

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.get("/")
def get_orders():
    return {"message": "orders route working"}
