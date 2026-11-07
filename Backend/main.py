from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from Backend.database import engine, Base, get_db
from Backend.models import Usuario
from Backend.auth import verificar_password, crear_access_token
from Backend.routers import alumnos, profesores, admin

# Creamos las tablas en la base de datos automáticamente si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SIVAN: Sistema de Control de Asistencias y Notificaciones",
    version="1.0.0",
    description="API REST para el control y prevención de faltas escolares con FastAPI y MySQL/PostgreSQL"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de cada módulo
app.include_router(alumnos.router, prefix="/api/alumnos", tags=["Alumnos"])
app.include_router(profesores.router, prefix="/api/profesores", tags=["Profesores"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administrador"])

# -----------------------------------------------------------------
# ENDPOINT DE AUTENTICACIÓN (LOGIN)
# -----------------------------------------------------------------
@app.post("/token", tags=["Autenticación"])
def login_para_obtener_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Recibe el email (en el campo username) y password del usuario.
    Valida las credenciales y devuelve un token de acceso JWT.
    """
    # Buscamos al usuario por su email
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    if not usuario or not verificar_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Creamos el token JWT incluyendo el correo en el 'sub'
    access_token = crear_access_token(data={"sub": usuario.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": usuario.id,
        "nombre": f"{usuario.nombre} {usuario.apellido}",
        "rol_id": usuario.rol_id
    }

@app.get("/")
def read_root():
    return {
        "mensaje": "Bienvenido al backend de SIVAN (Sistema de Control de Asistencias)",
        "documentacion": "/docs",
        "estado": "Activo"
    }