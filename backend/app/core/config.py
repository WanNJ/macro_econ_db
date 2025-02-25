import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "宏观经济数据智能系统"
    API_V1_STR: str = "/api"

    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://macro_user:macro_pass@localhost:5433/macro_econ"
    )


settings = Settings()
