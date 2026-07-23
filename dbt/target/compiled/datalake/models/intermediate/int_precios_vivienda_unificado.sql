

-- Resuelve id_geografia vía slug_tinsa (URL), NUNCA por el texto de zona
-- (ambiguo: "Málaga" aparece como provincia y como municipio).
SELECT
    sgt.id_geografia,
    t.anio,
    t.trimestre,
    t.precio_m2
FROM "postgres"."staging"."stg_precios_tinsa" t
LEFT JOIN "postgres"."reference"."seed_geografia_tinsa" sgt ON COALESCE(t.slug_tinsa, '') = COALESCE(sgt.slug_tinsa, '')