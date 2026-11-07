from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Literal
from Backend.database import get_db
from Backend.models import Usuario, SesionClase, Asistencia, Inscripcion
from Backend.auth import obtener_usuario_actual

router = APIRouter()

class AsistenciaRegistro(BaseModel):
    alumno_id: int
    estado: Literal["presente", "falta", "retardo", "justificado"]

class SesionAsistenciaRequest(BaseModel):
    grupo_id: int
    parcial_id: int
    fecha: str
    asistencias: List[AsistenciaRegistro]


@router.post("/registrar-asistencia")
def registrar_asistencia_clase(
    datos: SesionAsistenciaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Permite al profesor registrar o actualizar el pase de lista de una sesión de clase.
    """
    # 1. Validar que el usuario sea profesor o admin
    if current_user.rol_id not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para registrar asistencias."
        )

    # 2. Crear la Sesión de Clase
    nueva_sesion = SesionClase(
        grupo_id=datos.grupo_id,
        parcial_id=datos.parcial_id,
        fecha=datos.fecha,
        profesor_id=current_user.id
    )
    db.add(nueva_sesion)
    db.commit()
    db.refresh(nueva_sesion)

    # 3. Registrar el estado de asistencia de cada alumno
    registros_guardados = 0
    for item in datos.asistencias:
        # Verificar que el alumno esté inscrito en el grupo
        inscrito = db.query(Inscripcion).filter(
            Inscripcion.alumno_id == item.alumno_id,
            Inscripcion.grupo_id == datos.grupo_id
        ).first()

        if inscrito:
            nueva_asistencia = Asistencia(
                sesion_id=nueva_sesion.id,
                alumno_id=item.alumno_id,
                estado=item.estado
            )
            db.add(nueva_asistencia)
            registros_guardados += 1

    db.commit()

    return {
        "mensaje": "Asistencia registrada correctamente",
        "sesion_id": nueva_sesion.id,
        "total_registros": registros_guardados
    }
