"""
Registra los deployments en Prefect Server (Prefect 3.x).

Ejecutar UNA SOLA VEZ tras levantar el worker:
    PREFECT_API_URL=${PREFECT_API_URL} uv run python flows/deploy.py

Después puedes lanzar flows desde la UI en http://localhost:4200
"""
#deployment ejecuta un flow en un workpool
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "src")

from prefect.client.orchestration import get_client
from prefect.client.schemas.actions import DeploymentScheduleCreate
from prefect.client.schemas.schedules import CronSchedule

from champion_promotion import champion_promotion_flow
from retraining_trigger import retraining_trigger_flow
from training_pipeline import training_pipeline_flow

WORK_POOL = "churn-process-pool"
# El worker Docker monta el repo en /app; localmente el path es la raíz del repo.
# Si PREFECT_WORKER_PATH está seteado, lo usa (para workers en Docker).
import os as _os
REPO_ROOT = _os.environ.get("PREFECT_WORKER_PATH", str(Path(__file__).parent.parent.resolve()))


async def ensure_work_pool():#verifica si hay un workpool sino la crea
    async with get_client() as client:
        try:
            await client.read_work_pool(WORK_POOL)
            print(f"Work pool '{WORK_POOL}' already exists")
        except Exception:
            await client.create_work_pool(
                work_pool={"name": WORK_POOL, "type": "process"}
            )
            print(f"Created work pool '{WORK_POOL}'")


async def get_or_create_flow_id(client, flow):
    """Register the flow object and return its server ID."""
    return await client.create_flow(flow)


async def deploy_flow(client, flow, name: str, parameters: dict, schedules: list = None):
    flow_id = await get_or_create_flow_id(client, flow)

    schedule_creates = []
    if schedules:
        for sched in schedules:
            schedule_creates.append(
                DeploymentScheduleCreate(schedule=sched, active=True)
            )

    deployment_id = await client.create_deployment(
        flow_id=flow_id,
        name=name,
        parameters=parameters,
        work_pool_name=WORK_POOL,
        work_queue_name="default",
        path=REPO_ROOT,
        entrypoint=f"flows/{flow.fn.__code__.co_filename.split('flows/')[-1]}:{flow.fn.__name__}",
        schedules=schedule_creates,
    )
    return deployment_id


async def main():
    await ensure_work_pool()

    async with get_client() as client:
        dep_id = await deploy_flow(
            client,
            training_pipeline_flow,
            name="manual-training",
            parameters={"config_path": "configs/config.yaml", "model_type": "xgboost"},
        )
        print(f"Deployment 'manual-training' registered — id={dep_id}")

        dep_id = await deploy_flow(
            client,
            retraining_trigger_flow,
            name="daily-retraining",
            parameters={"config_path": "configs/config.yaml", "max_age_days": 7},
            schedules=[CronSchedule(cron="0 2 * * *", timezone="Europe/Madrid")],
        )
        print(f"Deployment 'daily-retraining' registered — id={dep_id}")

        dep_id = await deploy_flow(
            client,
            champion_promotion_flow,
            name="auto-promotion",
            parameters={"config_path": "configs/config.yaml", "threshold": 0.005},
        )
        print(f"Deployment 'auto-promotion' registered — id={dep_id}")

    print("\nAll deployments registered. Open http://localhost:4200 to run them.")


if __name__ == "__main__":
    asyncio.run(main())
