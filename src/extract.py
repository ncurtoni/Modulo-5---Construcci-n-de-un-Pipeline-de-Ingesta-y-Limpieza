"""
Modulo de extraccion (Extract).
Pide a la API de Jolpica-F1 el historial de resultados de un piloto,
guarda una copia cruda tal cual llega, y devuelve un DataFrame con los
tipos de datos ya optimizados para las etapas siguientes.
"""

import os
import requests
import pandas as pd

DRIVER_ID = os.getenv("DRIVER_ID", "colapinto")
BASE_URL = os.getenv("JOLPICA_BASE_URL", "http://api.jolpi.ca/ergast/f1")


def obtener_resultados_crudos(driver_id, base_url):
    """Pide los resultados de carrera del piloto y arma una tabla plana, sin tipar."""
    url = f"{base_url}/drivers/{driver_id}/results.json"
    response = requests.get(url, params={"limit": 100}, timeout=10)
    response.raise_for_status()

    carreras = response.json()["MRData"]["RaceTable"]["Races"]

    filas = []
    for carrera in carreras:
        resultado = carrera["Results"][0]
        filas.append({
            "season": carrera["season"],
            "round": carrera["round"],
            "race_name": carrera["raceName"],
            "date": carrera["date"],
            "constructor": resultado["Constructor"]["name"],
            "grid": resultado["grid"],
            "position": resultado.get("position"),
            "points": resultado["points"],
            "status": resultado["status"],
        })

    return pd.DataFrame(filas)


def extract_data(driver_id=None, base_url=None, raw_output_path="data/raw/dataset.csv"):
    """
    Extrae los datos de la API, guarda el crudo en disco (tal cual, sin
    tipar) para poder compararlo mas adelante contra el dataset procesado,
    y devuelve una version con los tipos ya optimizados.
    """
    driver_id = driver_id or DRIVER_ID
    base_url = base_url or BASE_URL

    df_crudo = obtener_resultados_crudos(driver_id, base_url)
    df_crudo.to_csv(raw_output_path, index=False)
    print(f"Dataset crudo guardado en: {raw_output_path} ({len(df_crudo)} filas)")

    df = df_crudo.copy()

    # season y round: enteros chicos, sin nulos esperados
    df["season"] = pd.to_numeric(df["season"], downcast="integer")
    df["round"] = pd.to_numeric(df["round"], downcast="integer")

    # grid: entero chico, casi nunca nulo
    df["grid"] = pd.to_numeric(df["grid"], downcast="integer")

    # position: puede venir vacio si el piloto no clasifico (abandono).
    # Se usa Int64 (con mayuscula, el "entero que admite nulos" de pandas)
    # en vez del int comun, porque un int normal no puede contener NaN.
    df["position"] = pd.to_numeric(df["position"], errors="coerce").astype("Int64")

    # points: siempre numerico, downcast a float chico
    df["points"] = pd.to_numeric(df["points"], downcast="float")

    # texto con pocos valores distintos, se repite en cada fila
    df["constructor"] = df["constructor"].astype("category")
    df["status"] = df["status"].astype("category")

    df["date"] = pd.to_datetime(df["date"])

    return df

