from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crea el motor de la base de datos, que gestiona la conexión con MySQL
engine = create_engine(DATABASE_URL, echo=False)

# Clase base para los modelos ORM de SQLAlchemy
Base = declarative_base()

# Crea una clase de sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener una sesión de base de datos en cada request
def get_db():
    db = SessionLocal()  # Crea una nueva sesión
    try:
        yield db         # La sesión se usa en el endpoint
        # yield significa: "devuelve la sesión y espera a que se complete el bloque"
    finally:
        db.close()       # Cierra la sesión al finalizar
