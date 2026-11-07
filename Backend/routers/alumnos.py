from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from Backend.database import get_db
from Backend.models import Usuario, Inscripcion, Grupo, SesionClase, Asistencia, Parcial
from Backend.auth import obtener_usuario_actual, verificar_rol

router = APIRouter()

@router.get("/mis-asistencias/{grupo_id}")
def consultar_asistencias_alumno(
    grupo_id: int,
    parcial_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Permite al alumno consultar sus asistencias, faltas y el semáforo de riesgo 
    para un grupo y parcial específico (o acumulado).
    """
    # 1. Verificar que el usuario sea alumno (o admin/profesor consultando)
    # Validamos que esté inscrito en el grupo
    inscripcion = db.query(Inscripcion).filter(
        Inscripcion.alumno_id == current_user.id,
        Inscripcion.grupo_id == grupo_id
    ).first()

    if not inscripcion and current_user.rol_id == 3: # Si es alumno y no está inscrito
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás inscrito en este grupo."
        )

    # 2. Construir la consulta de clases y asistencias
    query = db.query(
        func.count(SesionClase.id).label("clases_impartidas"),
        func.sum(func.case((Asistencia.estado == 'presente', 1), else_=0)).label("presentes"),
        func.sum(func.case((Asistencia.estado == 'retardo', 1), else_=0)).label("retardos"),
        func.sum(func.case((Asistencia.estado == 'falta', 1), else_=0)).label("faltas"),
    ).join(SesionClase, SesionClase.grupo_id == grupo_id) \
     .outerjoin(Asistencia, (Asistencia.sesion_id == SesionClase.id) & (Asistencia.alumno_id == current_user.id)) \
     .filter(SesionClase.grupo_id == grupo_id)

    if parcial_id:
        query = query.filter(SesionClase.parcial_id == parcial_id)

    resultado = query.first()

    clases = resultado.clases_impartidas or 0
    presentes = resultado.presentes or 0
    retardos = resultado.retardos or 0
    faltas = resultado.faltas or 0

    # 3. Calcular porcentaje de faltas y semáforo de riesgo
    porcentaje_faltas = (faltas / clases * 100) if clases > 0 else 0.0

    if porcentaje_faltas >= 25:
        semaforo = "Sin Derecho (Negro)"
    elif porcentaje_faltas >= 20:
        semaforo = "Riesgo Crítico (Rojo)"
    elif porcentaje_faltas >= 11:
        semaforo = "Riesgo Moderado (Amarillo)"
    else:
        semaforo = "Sin Riesgo (Verde)"

    return {
        "alumno_id": current_user.id,
        "nombre": f"{current_user.nombre} {current_user.apellido}",
        "grupo_id": grupo_id,
        "clases_impartidas": clases,
        "asistencias_presentes": presentes,
        "retardos": retardos,
        "faltas": faltas,
        "porcentaje_faltas": round(porcentaje_faltas, 2),
        "semaforo_riesgo": semaforo
    }