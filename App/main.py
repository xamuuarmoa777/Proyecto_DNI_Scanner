from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

from . import models, crud
from .database import engine, SessionLocal, Base


# Crear tablas en MariaDB
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# DEPENDENCIA DB
# -------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------
# Pydantic Schemas
# -------------------------------
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


class ScanData(BaseModel):
    raw: str


# -------------------------------
# RUTAS CRUD PERSONAS
# -------------------------------
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


# -------------------------------
# RUTA /scan (PDF417)
# -------------------------------
@app.post("/personas/scan")
def scan_persona(data: ScanData):
    raw = data.raw
    partes = raw.split('@')

    if len(partes) < 8:
        raise HTTPException(status_code=400, detail="PDF417 inválido")

    apellido = partes[1]
    nombre = partes[2]
    genero = partes[7]
    dni = partes[4]
    fecha = partes[6]

    fecha_formato = f"{fecha[0:4]}-{fecha[4:6]}-{fecha[6:8]}"

    persona = {
        "nombre": nombre,
        "apellido": apellido,
        "genero": genero,
        "dni": dni,
        "fecha_nacimiento": fecha_formato
    }

    return persona

