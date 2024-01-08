from pydantic import BaseModel, validator
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Optional

Base = declarative_base()
SQLALCHEMY_DATABASE_URL = "postgresql://zrch:password@postgres/car_management"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


class ListingStatus:
    INACTIVE = "inactive"
    ACTIVE = "active"
    SOLD = "sold"

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, Sequence("car_id_seq"), primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)
    color = Column(String, index=True)
    mileage = Column(Integer)
    broker_id = Column(Integer, ForeignKey('brokers.id'))
    broker = relationship("Broker", back_populates="cars")
    listing_status = Column(String, default=ListingStatus.INACTIVE)

class Broker(Base):
    __tablename__ = "brokers"
    id = Column(Integer, Sequence("broker_id_seq"), primary_key=True, index=True)
    name = Column(String, index=True)
    branches = Column(String, index=True)
    mobile_phone = Column(String, index=True)
    email = Column(String, index=True)
    cars = relationship("Car", back_populates="broker")

class CarModel(BaseModel):
    brand: str
    model: str
    year: int
    color: str
    mileage: int
    broker_id: Optional[int] = None
    listing_status: Optional[str] = None

    @validator("listing_status")
    def validate_listing_status(cls, value):
        valid_statuses = {ListingStatus.INACTIVE, ListingStatus.ACTIVE, ListingStatus.SOLD}
        if value is not None and value not in valid_statuses:
            raise ValueError("Invalid listing_status. Must be one of: 'inactive', 'active', 'sold'")
        return value

class BrokerModel(BaseModel):
    name: str
    branches: str
    mobile_phone: str
    email: str

Base.metadata.create_all(bind=engine)