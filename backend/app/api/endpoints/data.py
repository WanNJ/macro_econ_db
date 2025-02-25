# backend/app/api/endpoints/data.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ...db.database import get_db
from ...db import crud, models
from ...services.data_collection.collectors import WorldBankCollector, IMFCollector
from ...services.analytics.analyzer import DataAnalyzer
from ...services.analytics.report_generator import ReportGenerator

router = APIRouter()


@router.get("/countries")
def get_countries(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """获取所有国家列表"""
    countries = crud.get_countries(db, skip=skip, limit=limit)
    return countries


@router.get("/indicators")
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
