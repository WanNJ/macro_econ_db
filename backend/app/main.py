# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.api import api_router
from .db.init_db import init_db

app = FastAPI(title="宏观经济数据智能系统")

# 允许CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加API路由
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "欢迎使用宏观经济数据智能系统API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# 启动时初始化数据库
@app.on_event("startup")
def startup_event():
    init_db()
