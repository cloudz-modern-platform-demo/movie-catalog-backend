"""SQLModel 테이블 정의"""
from typing import Optional
from sqlmodel import Field, SQLModel


class Theater(SQLModel, table=True):
    """영화관 테이블"""
    __tablename__ = "theater"
    
    id: str = Field(primary_key=True)
    name: str = Field(nullable=False)
    brand: str = Field(nullable=False)
    location: str = Field(nullable=False)
    operating_hours: str = Field(nullable=False)


class Movie(SQLModel, table=True):
    """영화 테이블"""
    __tablename__ = "movie"
    
    id: str = Field(primary_key=True)
    title: str = Field(nullable=False)
    distributor: str = Field(nullable=False)
    ticket_price: int = Field(ge=0, nullable=False)
    runtime_minutes: int = Field(ge=0, nullable=False)
    genre: str = Field(nullable=False)
    theater_id: str = Field(foreign_key="theater.id", nullable=False)

