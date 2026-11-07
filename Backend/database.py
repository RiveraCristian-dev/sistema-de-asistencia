from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------------------
# CONFIGURACIÓN DE CONEXIÓN
# -----------------------------------------------------------------
# 1. Desarrollo Local (MySQL):
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Mysqldb20@localhost/asistencia"

# 2. Producción / Migración futura (Neon PostgreSQL):
# Descomenta la siguiente línea cuando migres a Neon Postgres y ajusta tus credenciales:
# SQLALCHEMY_DATABASE_URL = "postgresql://usuario:password@ep-xxxx.us-east-1.aws.neon.tech/asistencia?sslmode=require"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la sesión de base de datos en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()