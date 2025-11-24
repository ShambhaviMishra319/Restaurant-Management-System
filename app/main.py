from fastapi import FastAPI
from app.database import Base, engine
from app.routers import items, orders, auth,reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant Management System")

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(orders.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"message": "Restaurant Management System API running!"}