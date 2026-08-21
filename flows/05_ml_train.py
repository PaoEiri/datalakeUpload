"""Flow de entrenamiento del modelo de predicción de precio_m2 (municipal).

Uso manual: docker exec -it prefect-worker python flows/05_ml_train.py
Ver consideraciones/instrucciones_ml_claude_code.md para el diseño completo.
"""
from prefect import flow, get_run_logger

from src.tasks.ml import (
    build_features,
    train_models,
    validate_walkforward,
    decide_gate,
    persist_model,
    forecast_recursivo,
)


@flow(name="ml-train-pipeline", log_prints=True)
def ml_train_pipeline():
    logger = get_run_logger()

    df = build_features()
    modelos = train_models(df)
    metricas = validate_walkforward(modelos, df)

    champion_algoritmo = decide_gate(metricas)

    if champion_algoritmo is None:
        logger.warning(
            "Gate no superado por ningún modelo — se mantiene el champion anterior activo "
            "(si existe). Revisa métricas/logs de ml-decide-gate para ajustar indicadores "
            "(pestaña Indicadores, columna 'Usar en ML') o hiperparámetros."
        )
        return

    modelo = modelos[champion_algoritmo]
    id_modelo = persist_model(modelo, metricas[champion_algoritmo], df)
    forecast_recursivo(modelo, df, id_modelo, metricas[champion_algoritmo])

    logger.info(f"Pipeline de ML completado. Nuevo champion: {champion_algoritmo} (id_modelo={id_modelo}).")


if __name__ == "__main__":
    ml_train_pipeline()
