import re
import requests
import pandas as pd

# -------------------------------
# LISTA DE URLS A PROCESAR
# -------------------------------
urls = [
    "https://www.tinsa.es/precio-vivienda/andalucia/",
    "https://www.tinsa.es/precio-vivienda/andalucia/malaga/",
    "https://www.tinsa.es/precio-vivienda/andalucia/malaga/malaga/",
    "https://www.tinsa.es/precio-vivienda/"
]

# -------------------------------
# FUNCIÓN PARA EXTRAER DATOS DE UNA PÁGINA
# -------------------------------
def scrape_tinsa(url):
    html = requests.get(url).text

    # Buscar el bloque del gráfico principal (precio €/m²)
    pattern = r"var options = ({[\s\S]*?});\s*var chart = new ApexCharts\(document\.querySelector\(\"#grafica-imie-evolucion-precio-vivienda\""
    match = re.search(pattern, html)

    if not match:
        print(f"No se encontró gráfico principal en: {url}")
        return None

    js = match.group(1)

    # Nombre de la serie (barrio o ciudad)
    name_pattern = r"name:\s*'([^']+)'"
    name = re.search(name_pattern, js).group(1)

    # Valores
    data_pattern = r"data:\s*\[([^\]]+)\]"
    data_raw = re.search(data_pattern, js).group(1)
    values = [float(x.strip()) for x in data_raw.split(",")]

    # Periodos
    cat_pattern = r"categories:\s*\[([^\]]+)\]"
    cat_raw = re.search(cat_pattern, js).group(1)
    categories = [c.strip().strip("'") for c in cat_raw.split(",")]

    # Construir tabla
    df = pd.DataFrame({
        "zona": name,
        "periodo": categories,
        "valor": values,
        "url": url
    })

    return df

# -------------------------------
# PROCESAR TODAS LAS URLS
# -------------------------------
dfs = []

for url in urls:
    print(f"Procesando: {url}")
    df = scrape_tinsa(url)
    if df is not None:
        dfs.append(df)

# Unir todo
df_final = pd.concat(dfs, ignore_index=True)

# -------------------------------
# EXPORTAR A CSV
# -------------------------------
df_final.to_csv("tinsa_malaga_andalucia.csv", index=False, encoding="utf-8-sig")

print("CSV generado: tinsa_malaga_andalucia.csv")
