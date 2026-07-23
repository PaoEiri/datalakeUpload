"""Genera un diccionario de datos en Markdown a partir de dbt/target/{manifest,catalog}.json.

Requiere haber ejecutado antes `dbt docs generate` (o `dbt run` + `dbt docs generate`)
para que catalog.json refleje los tipos reales de columna en Postgres.
"""
from __future__ import annotations

import json
from pathlib import Path

TARGET_DIR = Path(__file__).resolve().parent.parent / "dbt" / "target"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "diccionario_datos.md"

LAYER_ORDER = ["staging", "intermediate", "core", "marts"]
LAYER_TITLES = {
    "staging": "Staging",
    "intermediate": "Intermediate",
    "core": "Core (dimensiones)",
    "marts": "Marts (hechos)",
}


def load_json(name: str) -> dict:
    with open(TARGET_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def model_layer(model_path: str) -> str:
    parts = Path(model_path).parts
    return parts[0] if parts and parts[0] in LAYER_ORDER else "otros"


def build_dictionary() -> str:
    manifest = load_json("manifest.json")
    catalog = load_json("catalog.json")

    catalog_nodes = {**catalog.get("nodes", {}), **catalog.get("sources", {})}

    models = {
        uid: node
        for uid, node in manifest["nodes"].items()
        if node.get("resource_type") == "model"
    }
    seeds = {
        uid: node
        for uid, node in manifest["nodes"].items()
        if node.get("resource_type") == "seed"
    }
    sources = {
        uid: node
        for uid, node in manifest.get("sources", {}).items()
    }

    by_layer: dict[str, list[tuple[str, dict]]] = {layer: [] for layer in LAYER_ORDER}
    for uid, node in models.items():
        layer = model_layer(node["path"])
        by_layer.setdefault(layer, []).append((uid, node))

    lines: list[str] = []
    lines.append("# Diccionario de datos")
    lines.append("")
    lines.append(
        "Generado automáticamente a partir de `dbt/target/manifest.json` y "
        "`dbt/target/catalog.json` (`dbt docs generate`). Los tipos de columna "
        "provienen del catálogo real de PostgreSQL; las descripciones, de los "
        "`schema.yml` del proyecto dbt."
    )
    lines.append("")

    if seeds:
        lines.append("## Seeds")
        lines.append("")
        for uid, node in sorted(seeds.items(), key=lambda t: t[1]["name"]):
            schema = node.get("schema", "?")
            name = node["name"]
            description = node.get("description") or "_Sin descripción._"
            lines.append(f"### `{schema}.{name}`")
            lines.append("")
            lines.append(description)
            lines.append("")

            cat_columns = catalog_nodes.get(uid, {}).get("columns", {})
            manifest_columns = node.get("columns", {})
            all_col_names = list(manifest_columns.keys())
            for col in cat_columns:
                if col not in all_col_names:
                    all_col_names.append(col)

            if not all_col_names:
                lines.append("_Sin columnas documentadas._")
                lines.append("")
                continue

            lines.append("| Columna | Tipo | Descripción |")
            lines.append("|---|---|---|")
            for col in all_col_names:
                col_type = cat_columns.get(col, {}).get("type", "?")
                col_desc = manifest_columns.get(col, {}).get("description", "").strip() or "-"
                lines.append(f"| `{col}` | {col_type} | {col_desc} |")
            lines.append("")

    for layer in LAYER_ORDER:
        entries = sorted(by_layer.get(layer, []), key=lambda t: t[1]["name"])
        if not entries:
            continue
        lines.append(f"## {LAYER_TITLES[layer]}")
        lines.append("")

        for uid, node in entries:
            materialized = node.get("config", {}).get("materialized", "?")
            schema = node.get("schema", "?")
            name = node["name"]
            description = node.get("description") or "_Sin descripción._"

            lines.append(f"### `{schema}.{name}` ({materialized})")
            lines.append("")
            lines.append(description)
            lines.append("")

            cat_columns = catalog_nodes.get(uid, {}).get("columns", {})
            manifest_columns = node.get("columns", {})

            all_col_names = list(manifest_columns.keys())
            for col in cat_columns:
                if col not in all_col_names:
                    all_col_names.append(col)

            if not all_col_names:
                lines.append("_Sin columnas documentadas._")
                lines.append("")
                continue

            lines.append("| Columna | Tipo | Descripción |")
            lines.append("|---|---|---|")
            for col in all_col_names:
                col_type = cat_columns.get(col, {}).get("type", "?")
                col_desc = manifest_columns.get(col, {}).get("description", "").strip() or "-"
                lines.append(f"| `{col}` | {col_type} | {col_desc} |")
            lines.append("")

    lines.append("## Fuentes (`sources`)")
    lines.append("")
    for uid, node in sorted(sources.items(), key=lambda t: t[1]["name"]):
        schema = node.get("schema", "?")
        name = node["name"]
        description = node.get("description") or "_Sin descripción._"
        lines.append(f"### `{schema}.{name}`")
        lines.append("")
        lines.append(description)
        lines.append("")

        cat_columns = catalog_nodes.get(uid, {}).get("columns", {})
        manifest_columns = node.get("columns", {})
        all_col_names = list(manifest_columns.keys())
        for col in cat_columns:
            if col not in all_col_names:
                all_col_names.append(col)

        if not all_col_names:
            lines.append("_Sin columnas documentadas._")
            lines.append("")
            continue

        lines.append("| Columna | Tipo | Descripción |")
        lines.append("|---|---|---|")
        for col in all_col_names:
            col_type = cat_columns.get(col, {}).get("type", "?")
            col_desc = manifest_columns.get(col, {}).get("description", "").strip() or "-"
            lines.append(f"| `{col}` | {col_type} | {col_desc} |")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    content = build_dictionary()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"Diccionario de datos escrito en {OUTPUT_PATH}")
