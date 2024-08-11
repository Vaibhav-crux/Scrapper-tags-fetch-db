from fastapi import FastAPI

from app.routers import forbes

app = FastAPI()

app.include_router(forbes.router)
