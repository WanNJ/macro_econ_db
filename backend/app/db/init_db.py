# backend/app/db/init_db.py
from sqlalchemy.orm import Session
from .database import engine
from . import models
from ..core.config import settings


def init_db():
    # 创建所有表
    models.Base.metadata.create_all(bind=engine)

    # 初始化基础数据
    # ... (可以在这里添加初始化代码)


if __name__ == "__main__":
    init_db()
