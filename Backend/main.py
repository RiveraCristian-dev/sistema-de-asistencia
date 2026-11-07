from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend.database import engine, Base
from Backend.routers import alumnos, profesores, admin

# Creamos las tablas en la base de datos automáticamente si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SIVAN: Sistema de Control de Asistencias y Notificaciones",
    version="1.0.0",
    description="API REST para el control y prevención de faltas escolares con FastAPI y MySQL/PostgreSQL"
)

# Configuración de CORS (permite la comunicación con el frontend HTML/JS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción puedes restringirlo a tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de cada módulo
app.include_router(alumnos.router, prefix="/api/alumnos", tags=["Alumnos"])
app.include_router(profesores.router, prefix="/api/profesores", tags=["Profesores"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administrador"])

@app.get("/")
def read_root():
    return {
        "mensaje": "Bienvenido al backend de SIVAN (Sistema de Control de Asistencias)",
        "documentacion": "/docs",
        "estado": "Activo"
    }