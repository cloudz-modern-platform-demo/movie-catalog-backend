"""Theater Pydantic 스키마"""
from typing import Optional
from pydantic import BaseModel, Field


class TheaterCreate(BaseModel):
    """영화관 생성 요청"""
    name: str
    brand: str
    location: str
    operating_hours: str


class TheaterUpdate(BaseModel):
    """영화관 수정 요청 (부분 업데이트)"""
    name: Optional[str] = None
    brand: Optional[str] = None
    location: Optional[str] = None
    operating_hours: Optional[str] = None


class TheaterRead(BaseModel):
    """영화관 응답"""
    id: str
    name: str
    brand: str
    location: str
    operating_hours: str
    
    model_config = {"from_attributes": True}

