
from sqlalchemy import Column, Integer, String, Date
from . database import Base

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    direccion = Column(String(100))
    genero = Column(String(10))
    fecha_nacimiento = Column(Date)

