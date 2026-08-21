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
    Numeric,
    String,
    Text,
    UniqueConstraint,
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


class MLModelRegistry(Base):
    __tablename__ = "ml_model_registry"
    __table_args__ = (CheckConstraint("algoritmo IN ('naive', 'ridge', 'xgboost')"),)

    id_modelo = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False)
    algoritmo = Column(String(20), nullable=False)
    fecha_entrenamiento = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    hiperparametros = Column(JSON, nullable=True)
    indicadores_usados = Column(JSON, nullable=True)
    importancia_features = Column(JSON, nullable=True)
    r2 = Column(Numeric(10, 6), nullable=True)
    accuracy_direccional = Column(Numeric(10, 6), nullable=True)
    rmse = Column(Numeric(18, 6), nullable=True)
    mae = Column(Numeric(18, 6), nullable=True)
    es_champion = Column(Boolean, nullable=False, default=False)
    ruta_minio_modelo = Column(String(300), nullable=True)
    ruta_minio_shap = Column(String(300), nullable=True)


class PrediccionMLRaw(Base):
    """Tabla operativa (no dbt) donde el flow de ML (flows/05_ml_train.py)
    escribe cada predicción. dbt la lee como source y la transforma en
    marts.fact_predicciones (dbt/models/marts/fact_predicciones.sql),
    resolviendo id_tiempo por join a dim_tiempo — por eso aquí no hace falta
    guardar id_tiempo, solo anio/trimestre."""
    __tablename__ = "predicciones_ml_raw"
    __table_args__ = (UniqueConstraint("id_geografia", "anio", "trimestre", "id_modelo"),)

    id_prediccion = Column(Integer, primary_key=True, index=True)
    id_geografia = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    id_modelo = Column(Integer, ForeignKey("ml_model_registry.id_modelo"), nullable=False)
    precio_predicho = Column(Numeric(18, 4), nullable=False)
    intervalo_inferior = Column(Numeric(18, 4), nullable=True)
    intervalo_superior = Column(Numeric(18, 4), nullable=True)
    es_forecast = Column(Boolean, nullable=False)
    creado_en = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
