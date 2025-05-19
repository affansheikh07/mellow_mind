from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.core.config import settings 
from fastapi.staticfiles import StaticFiles

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(auth_router)

app.include_router(auth_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "Welcome to Mellow Mind"}