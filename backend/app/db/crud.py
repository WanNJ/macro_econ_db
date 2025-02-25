from datetime import date
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from . import models


# Country CRUD操作
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


def update_country(
    db: Session, country_id: int, country_data: Dict
) -> Optional[models.Country]:
    db_country = get_country(db, country_id)
    if db_country:
        for key, value in country_data.items():
            setattr(db_country, key, value)
        db.commit()
        db.refresh(db_country)
    return db_country


def delete_country(db: Session, country_id: int) -> bool:
    db_country = get_country(db, country_id)
    if db_country:
        db.delete(db_country)
        db.commit()
        return True
    return False


# Indicator CRUD操作
def get_indicator(db: Session, indicator_id: int) -> Optional[models.Indicator]:
    return (
        db.query(models.Indicator).filter(models.Indicator.id == indicator_id).first()
    )


def get_indicator_by_code(db: Session, code: str) -> Optional[models.Indicator]:
    return db.query(models.Indicator).filter(models.Indicator.code == code).first()


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


def update_indicator(
    db: Session, indicator_id: int, indicator_data: Dict
) -> Optional[models.Indicator]:
    db_indicator = get_indicator(db, indicator_id)
    if db_indicator:
        for key, value in indicator_data.items():
            setattr(db_indicator, key, value)
        db.commit()
        db.refresh(db_indicator)
    return db_indicator


def delete_indicator(db: Session, indicator_id: int) -> bool:
    db_indicator = get_indicator(db, indicator_id)
    if db_indicator:
        db.delete(db_indicator)
        db.commit()
        return True
    return False


# DataSource CRUD操作
def get_data_source(db: Session, source_id: int) -> Optional[models.DataSource]:
    return db.query(models.DataSource).filter(models.DataSource.id == source_id).first()


def get_data_source_by_name(db: Session, name: str) -> Optional[models.DataSource]:
    return db.query(models.DataSource).filter(models.DataSource.name == name).first()


def get_data_sources(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.DataSource]:
    return db.query(models.DataSource).offset(skip).limit(limit).all()


def create_data_source(db: Session, source_data: Dict) -> models.DataSource:
    db_source = models.DataSource(**source_data)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


# DataPoint CRUD操作
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
