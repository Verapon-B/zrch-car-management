from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List

app = FastAPI()

# PostgreSQL Database Configuration
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgres/dbname"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SQLAlchemy Model for Car
class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, Sequence("car_id_seq"), primary_key=True, index=True)
    make = Column(String, index=True)
    model = Column(String, index=True)
    year = Column(Integer)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for input validation
class CarModel(BaseModel):
    make: str
    model: str
    year: int

# Pydantic model for the response of create_car endpoint
class CarResponse(BaseModel):
    id: int
    make: str
    model: str
    year: int

# CRUD Operations for Cars
@app.post("/cars/", response_model=CarResponse)
def create_car(car: CarModel):
    db_car = Car(make=car.make, model=car.model, year=car.year)
    with SessionLocal() as session:
        session.add(db_car)
        session.commit()
        session.refresh(db_car)
    return db_car

@app.get("/cars/", response_model=List[CarResponse])
def read_cars():
    with SessionLocal() as session:
        cars = session.query(Car).all()
        return cars

@app.get("/cars/{car_id}", response_model=CarResponse)
def read_car(car_id: int):
    with SessionLocal() as session:
        car = session.query(Car).filter(Car.id == car_id).first()
        if car:
            return car
        raise HTTPException(status_code=404, detail="Car not found")

@app.put("/cars/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car: CarModel):
    with SessionLocal() as session:
        db_car = session.query(Car).filter(Car.id == car_id).first()
        if db_car:
            for key, value in car.dict().items():
                setattr(db_car, key, value)
            session.commit()
            session.refresh(db_car)
            return db_car
        raise HTTPException(status_code=404, detail="Car not found")

@app.delete("/cars/{car_id}", response_model=CarResponse)
def delete_car(car_id: int):
    with SessionLocal() as session:
        db_car = session.query(Car).filter(Car.id == car_id).first()
        if db_car:
            session.delete(db_car)
            session.commit()
            return db_car
        raise HTTPException(status_code=404, detail="Car not found")

