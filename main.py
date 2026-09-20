import pandas as pd

from src.extract import extract_data
from src.transform import transform_data
from src.load import load_data

RUTA_CSV_ORIGEN = "data/raw/dataset.csv"  # se genera durante la extraccion
RUTA_PARQUET_DESTINO = "data/processed/dataset_procesado.parquet"


def validar_raw_vs_procesado(ruta_raw, ruta_procesado):
    """
    Compara el dataset crudo contra el procesado para confirmar que la
    limpieza realmente se aplico (no solo asumirlo).
    """
    df_raw = pd.read_csv(ruta_raw)
    df_procesado = pd.read_parquet(ruta_procesado)

    print(f"Filas      -> raw: {len(df_raw)} | procesado: {len(df_procesado)}")
    print(f"Columnas   -> raw: {len(df_raw.columns)} | procesado: {len(df_procesado.columns)} "
          f"(se agregaron 'no_clasifico' y 'posiciones_ganadas')")
    print(f"Duplicados -> raw: {df_raw.duplicated().sum()} | procesado: {df_procesado.duplicated().sum()}")
    print(f"Nulos en points -> raw: {df_raw['points'].isnull().sum()} | "
          f"procesado: {df_procesado['points'].isnull().sum()}")
    print(f"Tipo de season -> raw: {df_raw['season'].dtype} | procesado: {df_procesado['season'].dtype}")
    print(f"Tipo de constructor -> raw: {df_raw['constructor'].dtype} | "
          f"procesado: {df_procesado['constructor'].dtype}")


def main():
    print("Iniciando pipeline ETL...\n")

    print("Etapa 1: Extraccion")
    df = extract_data(raw_output_path=RUTA_CSV_ORIGEN)

    print("\nEtapa 2: Transformacion")
    df_transformado = transform_data(df)

    print("\nEtapa 3: Carga")
    load_data(df_transformado, RUTA_PARQUET_DESTINO)

    print("\nEtapa 4: Validacion (raw vs procesado)")
    validar_raw_vs_procesado(RUTA_CSV_ORIGEN, RUTA_PARQUET_DESTINO)

    print("\nPipeline ejecutado con exito.")


if __name__ == "__main__":
    main()
