from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from Backend.database import get_db
from Backend.models import Usuario, Grupo, Materia, Inscripcion
from Backend.auth import obtener_usuario_actual

router = APIRouter()

class GrupoCreate(BaseModel):
    nombre: str
    materia_id: int
    periodo_id: int
    profesor_id: int

class InscripcionCreate(BaseModel):
    alumno_id: int
    grupo_id: int


@router.post("/crear-grupo")
def crear_grupo(
    datos: GrupoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Permite al administrador crear un nuevo grupo escolar asignándole materia, periodo y profesor.
    """
    # Validar rol de administrador (rol_id == 1)
    if current_user.rol_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren privilegios de Administrador."
        )

    nuevo_grupo = Grupo(
        nombre=datos.nombre,
        materia_id=datos.materia_id,
        periodo_id=datos.periodo_id,
        profesor_id=datos.profesor_id
    )
    db.add(nuevo_grupo)
    db.commit()
    db.refresh(nuevo_grupo)

    return {
        "mensaje": "Grupo creado exitosamente",
        "grupo_id": nuevo_grupo.id,
        "nombre_grupo": nuevo_grupo.nombre
    }


@router.post("/inscribir-alumno")
def inscribir_alumno_grupo(
    datos: InscripcionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Inscribe a un alumno en un grupo específico para el control de asistencias.
    """
    if current_user.rol_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren privilegios de Administrador."
        )

    # Verificar si ya está inscrito
    existente = db.query(Inscripcion).filter(
        Inscripcion.alumno_id == datos.alumno_id,
        Inscripcion.grupo_id == datos.grupo_id
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El alumno ya se encuentra inscrito en este grupo."
        )

    nueva_inscripcion = Inscripcion(
        alumno_id=datos.alumno_id,
        grupo_id=datos.grupo_id
    )
    db.add(nueva_inscripcion)
    db.commit()

    return {
        "mensaje": "Alumno inscrito correctamente al grupo",
        "alumno_id": datos.alumno_id,
        "grupo_id": datos.grupo_id
    }