from prefect import flow
from src.tasks.dbt import run_dbt


@flow(name="dbt-pipeline", log_prints=True)
def dbt_pipeline(select: str | None = None):
    run_dbt(select=select)


if __name__ == "__main__":
    dbt_pipeline()