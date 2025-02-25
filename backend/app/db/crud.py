# backend/app/db/crud.py
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import date, datetime

from . import models


# 国家相关操作
def get_country(db: Session, country_id: int) -> Optional[models.Country]:
    return db.query(models.Country).filter(models.Country.id == country_id).first()


def get_country_by_code(db: Session, code: str) -> Optional[models.Country]:
    return db.query(models.Country).filter(models.Country.code == code).first()


def get_countries(db: Session, skip: int = 0, limit: int = 100) -> List[models.Country]:
    return db.query(models.Country).offset(skip).limit(limit).all()


def create_country(db: Session, country_data: Dict) -> models.Country:
    db_country = models.Country(**country_data)
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country


# 指标相关操作
def get_indicator(db: Session, indicator_id: int) -> Optional[models.Indicator]:
    return (
        db.query(models.Indicator).filter(models.Indicator.id == indicator_id).first()
    )


def get_indicator_by_code(db: Session, code: str) -> Optional[models.Indicator]:
    return db.query(models.Indicator).filter(models.Indicator.name == code).first()


def get_indicators(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Indicator]:
    return db.query(models.Indicator).offset(skip).limit(limit).all()


def create_indicator(db: Session, indicator_data: Dict) -> models.Indicator:
    db_indicator = models.Indicator(**indicator_data)
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    return db_indicator


# 数据源相关操作
def get_data_source(db: Session, source_id: int) -> Optional[models.DataSource]:
    return db.query(models.DataSource).filter(models.DataSource.id == source_id).first()


def get_data_source_by_name(db: Session, name: str) -> Optional[models.DataSource]:
    return db.query(models.DataSource).filter(models.DataSource.name == name).first()


def create_data_source(db: Session, source_data: Dict) -> models.DataSource:
    db_source = models.DataSource(**source_data)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


# 数据点相关操作
def create_data_point(db: Session, data_point: Dict) -> models.DataPoint:
    db_data_point = models.DataPoint(**data_point)
    db.add(db_data_point)
    db.commit()
    db.refresh(db_data_point)
    return db_data_point


def get_data_points(
    db: Session,
    country_id: Optional[int] = None,
    indicator_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 1000,
) -> List[models.DataPoint]:
    query = db.query(models.DataPoint)

    if country_id:
        query = query.filter(models.DataPoint.country_id == country_id)
    if indicator_id:
        query = query.filter(models.DataPoint.indicator_id == indicator_id)
    if start_date:
        query = query.filter(models.DataPoint.date >= start_date)
    if end_date:
        query = query.filter(models.DataPoint.date <= end_date)

    return query.offset(skip).limit(limit).all()
