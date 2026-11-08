from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from Backend.database import get_db
from Backend.models import Usuario, Grupo, Materia, Inscripcion
from Backend.auth import obtener_usuario_actual

router = APIRouter()

class GrupoCreate(BaseModel):
    nombre: str
    
    periodo_parcial: int
    materia_id: int
    profesor_id: int

class InscripcionCreate(BaseModel):
    matricula: str
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
        codigo_grupo=datos.nombre,
        periodo_id=datos.periodo_parcial, 
        materia_id=datos.materia_id,
        profesor_id=datos.profesor_id,
        total_clases_estimadas=16  # <--- Agregamos este valor para cumplir con la base de datos
    )
    db.add(nuevo_grupo)
    db.commit()
    db.refresh(nuevo_grupo)

    return {
        "mensaje": "Grupo creado exitosamente",
        "grupo_id": nuevo_grupo.id,
        "nombre_grupo": nuevo_grupo.codigo_grupo  # <--- Corregido de .nombre a .codigo_grupo
    }
@router.post("/inscribir-alumno")
def inscribir_alumno_grupo(
    datos: InscripcionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Inscribe a un alumno en un grupo específico validando su ID/Matrícula.
    """
    if current_user.rol_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren privilegios de Administrador."
        )

    # 1. Buscar al alumno usando el número ingresado en la matrícula y rol_id = 3 (alumno)
    alumno = db.query(Usuario).filter(Usuario.id == datos.matricula, Usuario.rol_id == 3).first()

    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún alumno con la matrícula/ID '{datos.matricula}'."
        )

    # 2. Verificar si ya está inscrito usando el ID real del alumno (alumno.id)
    existente = db.query(Inscripcion).filter(
        Inscripcion.alumno_id == alumno.id,
        Inscripcion.grupo_id == datos.grupo_id
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El alumno ya se encuentra inscrito en este grupo."
        )

    # 3. Crear la inscripción usando alumno.id
    nueva_inscripcion = Inscripcion(
        alumno_id=alumno.id,
        grupo_id=datos.grupo_id
    )
    db.add(nueva_inscripcion)
    db.commit()

    return {
        "mensaje": f"¡Alumno con ID/Matrícula {datos.matricula} inscrito correctamente al grupo!",
        "alumno_id": alumno.id,
        "grupo_id": datos.grupo_id
    }



@router.get("/materias")
def listar_materias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """Devuelve el catálogo de materias para el panel de administración"""
    if current_user.rol_id != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    materias = db.query(Materia).all()
    return [{"id": m.id, "nombre": m.nombre} for m in materias]


@router.get("/profesores")
def listar_profesores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """Devuelve la lista de profesores (rol_id = 2) para asignar a grupos"""
    if current_user.rol_id != 1:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    profesores = db.query(Usuario).filter(Usuario.rol_id == 2).all()
    return [{"id": p.id, "nombre": f"{p.nombre} {p.apellido}"} for p in profesores]