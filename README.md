# FastAPI + MariaDB CRUD de Personas

## 📌 1. Instalación de dependencias
```bash
# Instalar FastAPI, Uvicorn, SQLAlchemy y MariaDB connector
pip install fastapi uvicorn sqlalchemy mariadb
```
# FrontEnd #

## Cambiar puerto de la aplicación ##

```bash
uvicorn frontend:app --reload --port 3001
```




```js
## 🏢 2. Estructura del proyecto 

```bash
app/
 ├── main.py
 ├── database.py
 ├── models.py
 └── crud.py
```

## ⚓ 3. DataBase:
```js
//database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Datos de conexión a MariaDB
DATABASE_URL = "mariadb+mariadbconnector://usuario:password@localhost:3306/mi_basedatos"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

```
## ⚓ 4. Modelos:
```js
//models.py
from sqlalchemy import Column, Integer, String, Date
from .database import Base

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    direccion = Column(String(100))
    genero = Column(String(10))
    fecha_nacimiento = Column(Date)

```

## 🚀 5. CRUD:

```js
//crud.py
from sqlalchemy.orm import Session
from . import models

def get_personas(db: Session):
    return db.query(models.Persona).all()

def get_persona(db: Session, persona_id: int):
    return db.query(models.Persona).filter(models.Persona.id == persona_id).first()

def create_persona(db: Session, persona: models.Persona):
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona

def update_persona(db: Session, persona_id: int, datos: dict):
    persona = db.query(models.Persona).filter(models.Persona.id == persona_id).first()
    if not persona:
        return None
    for key, value in datos.items():
        setattr(persona, key, value)
    db.commit()
    db.refresh(persona)
    return persona

def delete_persona(db: Session, persona_id: int):
    persona = db.query(models.Persona).filter(models.Persona.id == persona_id).first()
    if not persona:
        return None
    db.delete(persona)
    db.commit()
    return persona


```
## 💥6. Main:

```js
//main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from . import models, crud
from .database import engine, SessionLocal, Base

# Crear tablas en MariaDB
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependencia para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schema
class PersonaCreate(BaseModel):
    nombre: str
    apellido: str
    dni: str
    direccion: str | None = None
    genero: str | None = None
    fecha_nacimiento: date | None = None

class PersonaResponse(PersonaCreate):
    id: int

    class Config:
        orm_mode = True

# Rutas CRUD
@app.post("/personas/", response_model=PersonaResponse)
def crear_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    nueva = models.Persona(**persona.dict())
    return crud.create_persona(db, nueva)

@app.get("/personas/", response_model=list[PersonaResponse])
def listar_personas(db: Session = Depends(get_db)):
    return crud.get_personas(db)

@app.get("/personas/{persona_id}", response_model=PersonaResponse)
def obtener_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = crud.get_persona(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

@app.put("/personas/{persona_id}", response_model=PersonaResponse)
def actualizar_persona(persona_id: int, datos: PersonaCreate, db: Session = Depends(get_db)):
    persona = crud.update_persona(db, persona_id, datos.dict())
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

@app.delete("/personas/{persona_id}")
def eliminar_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = crud.delete_persona(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return {"detail": "Persona eliminada"}

```








