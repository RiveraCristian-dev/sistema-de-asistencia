from sqlalchemy import Column, Integer, String, Boolean, Date, Time, TIMESTAMP, Text, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .database import Base

class Rol(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    telefono = Column(String(20), nullable=True)  # Requerido para notificaciones móviles/WhatsApp[cite: 2]
    password_hash = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    activo = Column(Boolean, default=True)
    creado_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class Materia(Base):
    __tablename__ = "materias"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    creditos = Column(Integer, nullable=False)

class Periodo(Base):
    __tablename__ = "periodos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    activo = Column(Boolean, default=True)

class Parcial(Base):
    __tablename__ = "parciales"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    periodo_id = Column(Integer, ForeignKey("periodos.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(50), nullable=False)  # Ej. '1er Parcial', '2do Parcial'[cite: 2]
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    activo = Column(Boolean, default=True)

class Grupo(Base):
    __tablename__ = "grupos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    materia_id = Column(Integer, ForeignKey("materias.id", ondelete="CASCADE"), nullable=False)
    profesor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    periodo_id = Column(Integer, ForeignKey("periodos.id", ondelete="CASCADE"), nullable=False)
    codigo_grupo = Column(String(50), nullable=False)
    total_clases_estimadas = Column(Integer, nullable=False)

class Inscripcion(Base):
    __tablename__ = "inscripciones"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="CASCADE"), nullable=False)
    inscrito_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    __table_args__ = (UniqueConstraint('alumno_id', 'grupo_id', name='unique_alumno_grupo'),)

class SesionClase(Base):
    __tablename__ = "sesiones_clase"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="CASCADE"), nullable=False)
    parcial_id = Column(Integer, ForeignKey("parciales.id", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    creado_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class Asistencia(Base):
    __tablename__ = "asistencias"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sesion_id = Column(Integer, ForeignKey("sesiones_clase.id", ondelete="CASCADE"), nullable=False)
    alumno_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    estado = Column(String(20), nullable=False)  # 'presente', 'retardo', 'falta', 'justificado'
    registrado_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    __table_args__ = (UniqueConstraint('sesion_id', 'alumno_id', name='unique_sesion_alumno'),)

class NotificacionLog(Base):
    __tablename__ = "notificaciones_log"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(50), nullable=False)  # 'email', 'whatsapp'[cite: 2]
    mensaje = Column(Text, nullable=False)
    estado = Column(String(20), default="enviado")
    enviado_at = Column(TIMESTAMP, server_default=func.current_timestamp())