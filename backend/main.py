import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.exam_routes import router as exam_router
from backend.admin_routes import router as admin_router
from backend.exam_db import init_db

init_db()  # SQLite 自动建表

app = FastAPI(title="考证刷题助手")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exam_router)
app.include_router(admin_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
