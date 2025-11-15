from pydantic import BaseModel, Field


class MovieCreate(BaseModel):
    """Schema for creating a movie"""
    title: str
    distributor: str
    ticket_price: int = Field(ge=0)
    runtime_minutes: int = Field(ge=0)
    genre: str
    theater_id: str


class MovieUpdate(BaseModel):
    """Schema for updating a movie (partial updates allowed)"""
    title: str | None = None
    distributor: str | None = None
    ticket_price: int | None = Field(default=None, ge=0)
    runtime_minutes: int | None = Field(default=None, ge=0)
    genre: str | None = None
    theater_id: str | None = None


class MovieRead(BaseModel):
    """Schema for reading/returning movie data"""
    id: str
    title: str
    distributor: str
    ticket_price: int
    runtime_minutes: int
    genre: str
    theater_id: str

    class Config:
        from_attributes = True
