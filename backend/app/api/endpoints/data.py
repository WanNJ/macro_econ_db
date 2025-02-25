from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ...db.database import get_db
from ...db import crud, models
from ...db.schemas import Country, Indicator, DataSource, DataPoint

router = APIRouter()


@router.get("/countries", response_model=List[Country])
def get_countries(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """获取所有国家列表"""
    countries = crud.get_countries(db, skip=skip, limit=limit)
    return countries


@router.get("/countries/{country_id}", response_model=Country)
def get_country(country_id: int, db: Session = Depends(get_db)):
    """获取单个国家信息"""
    country = crud.get_country(db, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail="国家不存在")
    return country


@router.get("/indicators", response_model=List[Indicator])
def get_indicators(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """获取所有指标列表"""
    indicators = crud.get_indicators(db, skip=skip, limit=limit)
    return indicators


@router.get("/data_points")
def get_data_points(
    country_code: Optional[str] = None,
    indicator_code: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    """获取数据点"""
    country_id = None
    if country_code:
        country = crud.get_country_by_code(db, country_code)
        if country:
            country_id = country.id

    indicator_id = None
    if indicator_code:
        indicator = crud.get_indicator_by_code(db, indicator_code)
        if indicator:
            indicator_id = indicator.id

    data_points = crud.get_data_points(
        db,
        country_id=country_id,
        indicator_id=indicator_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    return data_points


@router.post("/init_data")
def initialize_data(db: Session = Depends(get_db)):
    """初始化示例数据（仅用于演示）"""
    from ...db.init_db import create_initial_data

    create_initial_data(db)
    return {"message": "初始化数据成功"}


@router.get("/query/{country_code}/{indicator_code}")
def query_data(
    country_code: str,
    indicator_code: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """查询特定国家和指标的数据"""
    country = crud.get_country_by_code(db, country_code)
    if not country:
        raise HTTPException(status_code=404, detail=f"国家代码不存在: {country_code}")

    indicator = crud.get_indicator_by_code(db, indicator_code)
    if not indicator:
        raise HTTPException(status_code=404, detail=f"指标代码不存在: {indicator_code}")

    # 设置日期范围
    start_date = None
    if start_year:
        start_date = date(start_year, 1, 1)

    end_date = None
    if end_year:
        end_date = date(end_year, 12, 31)

    # 获取数据
    data_points = crud.get_data_points(
        db,
        country_id=country.id,
        indicator_id=indicator.id,
        start_date=start_date,
        end_date=end_date,
    )

    # 格式化结果
    result = {
        "country": {"code": country.code, "name": country.name},
        "indicator": {
            "code": indicator.code,
            "name": indicator.name,
            "unit": indicator.unit,
        },
        "data": [{"year": dp.date.year, "value": dp.value} for dp in data_points],
    }

    return result
