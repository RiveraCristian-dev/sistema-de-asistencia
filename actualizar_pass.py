from Backend.database import SessionLocal
from Backend.models import Usuario
from Backend.auth import pwd_context

def actualizar_contraseñas():
    db = SessionLocal()
    try:
        # Buscamos a todos los usuarios de prueba
        usuarios = db.query(Usuario).all()
        for u in usuarios:
            # Generamos el hash oficial usando el mismo pwd_context del backend para la contraseña "123456"
            u.password_hash = pwd_context.hash("123456")
            print(f"Actualizando contraseña para: {u.email}")
        
        db.commit()
        print("¡Todas las contraseñas han sido actualizadas a '123456' exitosamente!")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    actualizar_contraseñas()