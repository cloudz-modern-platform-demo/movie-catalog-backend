from pydantic import BaseModel


class TheaterCreate(BaseModel):
    """Schema for creating a theater"""
    name: str
    brand: str
    location: str
    operating_hours: str


class TheaterUpdate(BaseModel):
    """Schema for updating a theater (partial updates allowed)"""
    name: str | None = None
    brand: str | None = None
    location: str | None = None
    operating_hours: str | None = None


class TheaterRead(BaseModel):
    """Schema for reading/returning theater data"""
    id: str
    name: str
    brand: str
    location: str
    operating_hours: str

    class Config:
        from_attributes = True
