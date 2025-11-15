"""Movie Pydantic 스키마"""
from typing import Optional
from pydantic import BaseModel, Field


class MovieCreate(BaseModel):
    """영화 생성 요청"""
    title: str
    distributor: str
    ticket_price: int = Field(ge=0)
    runtime_minutes: int = Field(ge=0)
    genre: str
    theater_id: str


class MovieUpdate(BaseModel):
    """영화 수정 요청 (부분 업데이트)"""
    title: Optional[str] = None
    distributor: Optional[str] = None
    ticket_price: Optional[int] = Field(default=None, ge=0)
    runtime_minutes: Optional[int] = Field(default=None, ge=0)
    genre: Optional[str] = None
    theater_id: Optional[str] = None


class MovieRead(BaseModel):
    """영화 응답"""
    id: str
    title: str
    distributor: str
    ticket_price: int
    runtime_minutes: int
    genre: str
    theater_id: str
    
    model_config = {"from_attributes": True}

