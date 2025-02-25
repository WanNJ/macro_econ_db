from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from .core.config import settings
from .db.database import get_db, engine
from .db.models import Base
from .api.api import api_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# 允许CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"message": f"欢迎使用{settings.PROJECT_NAME}"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-test")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "数据库连接成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")
