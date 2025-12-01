
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Datos de conexión a MariaDB
DATABASE_URL = "mariadb+mariadbconnector://root:1234@localhost:3306/mi_basedatos"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

