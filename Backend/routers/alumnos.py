from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_alumnos():
    return {"mensaje": "Endpoints de alumnos activos"}