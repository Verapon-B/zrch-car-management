from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Car, Broker, CarModel, BrokerModel
from typing import List

app = FastAPI()


SQLALCHEMY_DATABASE_URL = "postgresql://zrch:password@postgres/car_management"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/cars/", response_model=List[CarModel])
def get_all_cars():
    with SessionLocal() as session:
        cars = session.query(Car).all()
        return cars

@app.post("/cars/", response_model=CarModel)
def create_car(car: CarModel):
    with SessionLocal() as session:
        broker_id = car.broker_id
        if broker_id is not None:
            broker = session.query(Broker).filter(Broker.id == broker_id).first()
            if not broker:
                raise HTTPException(status_code=404, detail="Broker not found")
            else:
                car.broker = broker
        db_car = Car(**car.dict())
        session.add(db_car)
        session.commit()
        session.refresh(db_car)
    return db_car

@app.get("/cars/{car_id}", response_model=CarModel)
def read_car(car_id: int):
    with SessionLocal() as session:
        car = session.query(Car).filter(Car.id == car_id).first()
        if car:
            return car
        raise HTTPException(status_code=404, detail="Car not found")

@app.put("/cars/{car_id}", response_model=CarModel)
def update_car(car_id: int, car: CarModel):
    with SessionLocal() as session:
        db_car = session.query(Car).filter(Car.id == car_id).first()
        if not db_car:
            raise HTTPException(status_code=404, detail="Car not found")

        for key, value in car.dict().items():
            setattr(db_car, key, value)
        if car.broker_id and car.broker_id != None:
            broker = session.query(Broker).filter(Broker.id == car.broker_id).first()
            if not broker:
                raise HTTPException(status_code=404, detail="Broker not found")
            db_car.broker = broker

        session.commit()
        session.refresh(db_car)
        return db_car

@app.delete("/cars/{car_id}", response_model=CarModel)
def delete_car(car_id: int):
    with SessionLocal() as session:
        db_car = session.query(Car).filter(Car.id == car_id).first()
        if db_car:
            session.delete(db_car)
            session.commit()
            return db_car
        raise HTTPException(status_code=404, detail="Car not found")

@app.post("/brokers/", response_model=BrokerModel)
def create_broker(broker: BrokerModel):
    with SessionLocal() as session:
        db_broker = Broker(**broker.dict())
        session.add(db_broker)
        session.commit()
        session.refresh(db_broker)
    return db_broker

@app.get("/brokers/{broker_id}", response_model=BrokerModel)
def read_broker(broker_id: int):
    with SessionLocal() as session:
        broker = session.query(Broker).filter(Broker.id == broker_id).first()
        if broker:
            return broker
        raise HTTPException(status_code=404, detail="Broker not found")

@app.put("/brokers/{broker_id}", response_model=BrokerModel)
def update_broker(broker_id: int, broker: BrokerModel):
    with SessionLocal() as session:
        db_broker = session.query(Broker).filter(Broker.id == broker_id).first()
        if db_broker:
            for key, value in broker.dict().items():
                setattr(db_broker, key, value)
            session.commit()
            session.refresh(db_broker)
            return db_broker
        raise HTTPException(status_code=404, detail="Broker not found")

@app.delete("/brokers/{broker_id}", response_model=BrokerModel)
def delete_broker(broker_id: int):
    with SessionLocal() as session:
        db_broker = session.query(Broker).filter(Broker.id == broker_id).first()
        if db_broker:
            cars_to_update = session.query(Car).filter(Car.broker_id == broker_id).all()
            for car in cars_to_update:
                car.broker_id = None

            session.delete(db_broker)
            session.commit()
            return db_broker
        raise HTTPException(status_code=404, detail="Broker not found")

@app.get("/car_status/{status}", response_model=List[CarModel])
def get_cars_by_status(status: str):
    with SessionLocal() as session:
        cars = session.query(Car).filter(Car.listing_status == status).all()
        if cars:
            return cars
        raise HTTPException(status_code=404, detail=f"No cars found with status: {status}")