CREATE TABLE IF NOT EXISTS staging.ipv_precios_vivienda (
    id            SERIAL PRIMARY KEY,
    tipo_vivienda VARCHAR(50),
    ambito        VARCHAR(50),
    comunidad     VARCHAR(100),
    indicador     VARCHAR(100),
    anio          SMALLINT,
    trimestre     SMALLINT,
    fecha         DATE,         -- primer día del trimestre: 2025T4 → 2025-10-01
    valor         NUMERIC(12, 4),
    fuente        VARCHAR(200),
    cargado_en    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ipv_fecha
    ON staging.ipv_precios_vivienda (fecha);

CREATE INDEX IF NOT EXISTS idx_ipv_comunidad
    ON staging.ipv_precios_vivienda (comunidad);