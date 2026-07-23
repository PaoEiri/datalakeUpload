"""
Genera el diccionario de datos (Anexo A) a partir de los artefactos de
`dbt docs generate` (catalog.json + manifest.json).

Uso:
    python generate_data_dictionary.py catalog.json manifest.json > diccionario_datos.md

Requiere solo la librería estándar de Python (json, sys, collections).
"""
import json
import sys
from collections import defaultdict

# Orden de capas para que el documento salga organizado igual que el proyecto dbt
ORDEN_CAPAS = ["reference", "staging", "intermediate", "core", "marts"]


def capa_de(schema: str, nombre_modelo: str) -> str:
    """Determina la capa a partir del esquema/nombre del modelo."""
    esquema = (schema or "").lower()
    nombre = (nombre_modelo or "").lower()
    if esquema == "reference":
        return "reference"
    if nombre.startswith("stg_"):
        return "staging"
    if nombre.startswith("int_"):
        return "intermediate"
    if nombre.startswith("dim_"):
        return "core"
    if nombre.startswith("fact_"):
        return "marts"
    return "otros"


def main():
    if len(sys.argv) != 3:
        print("Uso: python generate_data_dictionary.py catalog.json manifest.json",
              file=sys.stderr)
        sys.exit(1)

    catalog_path, manifest_path = sys.argv[1], sys.argv[2]

    with open(catalog_path, encoding="utf-8") as f:
        catalog = json.load(f)
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    # manifest.json trae las descripciones definidas en schema.yml (modelo y columnas)
    nodos_manifest = {**manifest.get("nodes", {}), **manifest.get("sources", {})}

    # catalog.json trae las columnas y tipos reales tal como están en la base de datos
    nodos_catalog = {**catalog.get("nodes", {}), **catalog.get("sources", {})}

    por_capa = defaultdict(list)

    for unique_id, info_catalog in nodos_catalog.items():
        meta = info_catalog.get("metadata", {})
        nombre_modelo = meta.get("name", unique_id)
        schema = meta.get("schema", "")
        tipo_relacion = meta.get("type", "")  # 'view' o 'table' normalmente

        info_manifest = nodos_manifest.get(unique_id, {})
        descripcion_modelo = info_manifest.get("description", "").strip()
        columnas_manifest = info_manifest.get("columns", {})

        columnas = []
        for col_name, col_info in info_catalog.get("columns", {}).items():
            tipo_dato = col_info.get("type", "")
            descripcion_col = (
                columnas_manifest.get(col_name, {}).get("description", "").strip()
            )
            columnas.append({
                "nombre": col_name,
                "tipo": tipo_dato,
                "descripcion": descripcion_col,
            })

        # las columnas en catalog.json ya vienen ordenadas por posición física
        capa = capa_de(schema, nombre_modelo)
        por_capa[capa].append({
            "nombre": nombre_modelo,
            "schema": schema,
            "tipo_relacion": tipo_relacion,
            "descripcion": descripcion_modelo,
            "columnas": columnas,
        })

    # --- generar el Markdown ---
    print("## Anexo A. Diccionario de datos\n")

    capas_presentes = [c for c in ORDEN_CAPAS if c in por_capa] + \
                       [c for c in por_capa if c not in ORDEN_CAPAS]

    for capa in capas_presentes:
        modelos = sorted(por_capa[capa], key=lambda m: m["nombre"])
        print(f"### {capa.capitalize()}\n")
        for m in modelos:
            tipo = f" ({m['tipo_relacion']})" if m["tipo_relacion"] else ""
            print(f"**{m['schema']}.{m['nombre']}{tipo}**\n")
            if m["descripcion"]:
                print(f"{m['descripcion']}\n")
            if m["columnas"]:
                print("| Columna | Tipo | Descripción |")
                print("|---|---|---|")
                for c in m["columnas"]:
                    desc = c["descripcion"] or "-"
                    print(f"| {c['nombre']} | {c['tipo']} | {desc} |")
                print()
            else:
                print("_(sin columnas registradas en el catálogo)_\n")

    print(f"\n---\n*Diccionario generado automáticamente a partir de "
          f"catalog.json y manifest.json ({len(nodos_catalog)} relaciones documentadas).*")


if __name__ == "__main__":
    main()
