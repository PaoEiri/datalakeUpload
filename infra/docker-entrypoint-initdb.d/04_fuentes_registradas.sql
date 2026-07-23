-- Catálogo de fuentes registradas + versionado de datasets_upload.
-- Ver fuentes_registradas_y_api.md (raíz del repo) para el diseño completo.

ALTER TABLE public.datasets_upload
    ADD COLUMN IF NOT EXISTS vigente BOOLEAN NOT NULL DEFAULT TRUE;

CREATE TABLE IF NOT EXISTS public.fuentes_registradas (
    id_fuente                  SERIAL PRIMARY KEY,
    sistema_origen              VARCHAR(20) NOT NULL
        CHECK (sistema_origen IN ('INE', 'Tinsa', 'Ministerio')),
    codigo_fuente                VARCHAR(50) NOT NULL UNIQUE,
        -- ej. '69303', 'tinsa_precios', 'transacciones_libre'
    nivel_territorial            VARCHAR(20) NOT NULL
        CHECK (nivel_territorial IN ('Municipio', 'Distrito', 'Ambos', 'Multiescala')),
    stg_modelo_destino           VARCHAR(200) NOT NULL,
        -- nombre del modelo stg_*.sql que procesa esta fuente
    id_dataset_actual            INT REFERENCES public.datasets_upload(id),
        -- apunta a la fila vigente en datasets_upload; NULL si nunca se ha cargado
    fecha_ultima_actualizacion   TIMESTAMP,
    creado_en                    TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.fuentes_registradas_historial (
    id_historial            SERIAL PRIMARY KEY,
    id_fuente                INT NOT NULL REFERENCES public.fuentes_registradas(id_fuente),
    id_dataset_anterior      INT REFERENCES public.datasets_upload(id),
        -- NULL en la primera carga de una fuente (no había versión previa)
    id_dataset_nuevo         INT NOT NULL REFERENCES public.datasets_upload(id),
    fecha_cambio             TIMESTAMP NOT NULL DEFAULT now()
);

INSERT INTO public.fuentes_registradas
    (sistema_origen, codigo_fuente, nivel_territorial, stg_modelo_destino)
VALUES
    ('INE', '31106', 'Ambos',     'stg_indicadores_renta_persona_hogar'),
    ('INE', '31114', 'Ambos',     'stg_indicadores_demograficos'),
    ('INE', '31107', 'Ambos',     'stg_indicadores_fuente_ingreso'),
    ('INE', '37706', 'Ambos',     'stg_indicadores_gini_p80p20'),
    ('INE', '2882',  'Municipio', 'stg_poblacion_sexo'),
    ('INE', '69303', 'Municipio', 'stg_indicadores_malaga'),
    ('INE', '69301', 'Municipio', 'stg_indicadores_demograficos_actualizado'),
    ('INE', '69307', 'Municipio', 'stg_indicadores_turismo'),

    ('Tinsa', 'tinsa_precios', 'Multiescala', 'stg_precios_tinsa'),

    ('Ministerio', 'transacciones_libre',        'Municipio', 'stg_transacciones_libre'),
    ('Ministerio', 'transacciones_segunda_mano',  'Municipio', 'stg_transacciones_segunda_mano'),
    ('Ministerio', 'transacciones_nueva',         'Municipio', 'stg_transacciones_nueva'),
    ('Ministerio', 'transacciones_protegida',     'Municipio', 'stg_transacciones_protegida')
ON CONFLICT (codigo_fuente) DO NOTHING;
