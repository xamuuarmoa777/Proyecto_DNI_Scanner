
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

def get_persona_by_dni(db, dni: str):
    return db.query(models.Persona).filter(models.Persona.dni == dni).first()



