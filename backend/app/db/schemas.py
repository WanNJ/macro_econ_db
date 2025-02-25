from pydantic import BaseModel
from datetime import date
from typing import Optional


# 国家模式
class CountryBase(BaseModel):
    name: str
    code: str
    region: Optional[str] = None


class CountryCreate(CountryBase):
    pass


class Country(CountryBase):
    id: int

    class Config:
        orm_mode = True


# 指标模式
class IndicatorBase(BaseModel):
    name: str
    code: str
    category: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None


class IndicatorCreate(IndicatorBase):
    pass


class Indicator(IndicatorBase):
    id: int

    class Config:
        orm_mode = True


# 数据源模式
class DataSourceBase(BaseModel):
    name: str
    url: Optional[str] = None
    reliability_score: Optional[float] = None
    last_updated: Optional[date] = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSource(DataSourceBase):
    id: int

    class Config:
        orm_mode = True


# 数据点模式
class DataPointBase(BaseModel):
    date: date
    value: float


class DataPointCreate(DataPointBase):
    country_id: int
    indicator_id: int
    source_id: int


class DataPoint(DataPointBase):
    id: int
    country_id: int
    indicator_id: int
    source_id: int

    class Config:
        orm_mode = True
