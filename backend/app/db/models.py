# backend/app/db/models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True)
    region = Column(String)


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    unit = Column(String)
    description = Column(Text)


class DataPoint(Base):
    __tablename__ = "data_points"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"))
    indicator_id = Column(Integer, ForeignKey("indicators.id"))
    date = Column(Date, index=True)
    value = Column(Float)
    source_id = Column(Integer, ForeignKey("data_sources.id"))


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    url = Column(String)
    reliability_score = Column(Float)
    last_updated = Column(Date)
