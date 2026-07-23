import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from .database import Base


class Dataset(Base):
    __tablename__ = "datasets_upload"

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(255), unique=True, nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    storage_key = Column(String(512), nullable=False)
    file_format = Column(String(50), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    schema = Column(JSON, nullable=True)
    preview = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    vigente = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )


class FuenteRegistrada(Base):
    __tablename__ = "fuentes_registradas"
    __table_args__ = (
        CheckConstraint("sistema_origen IN ('INE', 'Tinsa', 'Ministerio')"),
        CheckConstraint(
            "nivel_territorial IN ('Municipio', 'Distrito', 'Ambos', 'Multiescala')"
        ),
    )

    id_fuente = Column(Integer, primary_key=True, index=True)
    sistema_origen = Column(String(20), nullable=False)
    codigo_fuente = Column(String(50), unique=True, nullable=False, index=True)
    nivel_territorial = Column(String(20), nullable=False)
    stg_modelo_destino = Column(String(200), nullable=False)
    id_dataset_actual = Column(Integer, ForeignKey("datasets_upload.id"), nullable=True)
    fecha_ultima_actualizacion = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class FuenteRegistradaHistorial(Base):
    __tablename__ = "fuentes_registradas_historial"

    id_historial = Column(Integer, primary_key=True, index=True)
    id_fuente = Column(Integer, ForeignKey("fuentes_registradas.id_fuente"), nullable=False)
    id_dataset_anterior = Column(Integer, ForeignKey("datasets_upload.id"), nullable=True)
    id_dataset_nuevo = Column(Integer, ForeignKey("datasets_upload.id"), nullable=False)
    fecha_cambio = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
