from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import Usuario

# Configuración de seguridad
SECRET_KEY = "clave_secreta_super_segura_sivan_2026"  # En producción usa una variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # El token dura 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funciones de Contraseña
validador_pwd = pwd_context

def verificar_password(plain_password, hashed_password):
    return validador_pwd.verify(plain_password, hashed_password)

def obtener_password_hash(password):
    return validador_pwd.hash(password)

# Crear Token JWT
def crear_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Obtener usuario autenticado actual a partir del Token
def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise credentials_exception
    return usuario

# Control de acceso por roles (Validación estricta en el servidor)
def verificar_rol(rol_requerido: str):
    def role_dependency(usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
        # Buscamos el nombre del rol del usuario
        from .models import Rol
        rol_obj = db.query(Rol).filter(Rol.id == usuario.rol_id).first()
        if not rol_obj or rol_obj.nombre != rol_requerido:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere el rol de: {rol_requerido}"
            )
        return usuario
    return role_dependency