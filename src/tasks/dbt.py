from __future__ import annotations

import subprocess
from prefect import task, get_run_logger

from src.config import settings


@task(name="dbt-run", retries=0)
def run_dbt(select: str | None = None) -> str:
    logger = get_run_logger()

    cmd = [
        "dbt", "run",
        "--project-dir", settings.dbt_project_dir,
        "--profiles-dir", settings.dbt_profiles_dir,
        "--target", settings.dbt_target,
    ]
    if select:
        cmd += ["--select", select]

    logger.info(f"Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    logger.info(f"STDOUT: {result.stdout}")
    logger.info(f"STDERR: {result.stderr}")
    logger.info(f"Return code: {result.returncode}")

    if result.returncode != 0:
        raise RuntimeError(f"dbt run falló:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

    return result.stdout