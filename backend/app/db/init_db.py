from sqlalchemy.orm import Session
from .database import engine, Base
from .models import Country, Indicator, DataSource, DataPoint
from datetime import datetime


def init_db():
    """初始化数据库表结构和基础数据"""
    # 创建表
    Base.metadata.create_all(bind=engine)

    # 添加基础数据可以在这里实现
    # 比如添加一些常见的国家和指标


def create_initial_data(db: Session):
    """创建初始数据（演示用）"""
    # 检查是否已经有数据
    if db.query(Country).count() > 0:
        return

    # 添加一些国家
    countries = [
        {"name": "中国", "code": "CHN", "region": "亚洲"},
        {"name": "美国", "code": "USA", "region": "北美洲"},
        {"name": "日本", "code": "JPN", "region": "亚洲"},
        {"name": "德国", "code": "DEU", "region": "欧洲"},
        {"name": "印度", "code": "IND", "region": "亚洲"},
    ]

    for country_data in countries:
        country = Country(**country_data)
        db.add(country)

    # 添加一些指标
    indicators = [
        {
            "name": "国内生产总值",
            "code": "GDP",
            "category": "经济",
            "unit": "美元",
            "description": "国内生产总值是一个国家在特定时期内生产的所有成品和服务的市场价值",
        },
        {
            "name": "消费者物价指数",
            "code": "CPI",
            "category": "经济",
            "unit": "%",
            "description": "消费者物价指数是衡量一篮子消费品和服务价格随时间变化的指标",
        },
        {
            "name": "失业率",
            "code": "UNEMP",
            "category": "劳动力",
            "unit": "%",
            "description": "失业率是劳动力中未就业人口所占的百分比",
        },
    ]

    for indicator_data in indicators:
        indicator = Indicator(**indicator_data)
        db.add(indicator)

    # 添加数据源
    sources = [
        {
            "name": "世界银行",
            "url": "https://data.worldbank.org/",
            "reliability_score": 0.9,
            "last_updated": datetime.now().date(),
        },
        {
            "name": "国际货币基金组织",
            "url": "https://www.imf.org/en/Data",
            "reliability_score": 0.85,
            "last_updated": datetime.now().date(),
        },
    ]

    for source_data in sources:
        source = DataSource(**source_data)
        db.add(source)

    # 提交事务
    db.commit()
