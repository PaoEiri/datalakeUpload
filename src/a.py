from prefect import flow, task  

@flow(name="hola-mundo", log_prints=True)
def main(mensaje:str):
    hola=hola_mundo(mensaje)
    return hola
@task()
def hola_mundo(mensaje:str):
    return f"Hola {mensaje}!"

if __name__ == "__main__":
    main("Prefect")
  