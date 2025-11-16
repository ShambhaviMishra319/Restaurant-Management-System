from fastapi import APIRouter

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

@router.get("/")
def get_items():
    return {"message": "items route working"}
