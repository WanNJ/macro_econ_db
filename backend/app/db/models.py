from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True, index=True)
    region = Column(String)

    # 关系
    data_points = relationship("DataPoint", back_populates="country")


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    unit = Column(String)
    description = Column(Text)

    # 关系
    data_points = relationship("DataPoint", back_populates="indicator")


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    url = Column(String)
    reliability_score = Column(Float)
    last_updated = Column(Date)

    # 关系
    data_points = relationship("DataPoint", back_populates="source")


class DataPoint(Base):
    __tablename__ = "data_points"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"))
    indicator_id = Column(Integer, ForeignKey("indicators.id"))
    date = Column(Date, index=True)
    value = Column(Float)
    source_id = Column(Integer, ForeignKey("data_sources.id"))

    # 关系
    country = relationship("Country", back_populates="data_points")
    indicator = relationship("Indicator", back_populates="data_points")
    source = relationship("DataSource", back_populates="data_points")
