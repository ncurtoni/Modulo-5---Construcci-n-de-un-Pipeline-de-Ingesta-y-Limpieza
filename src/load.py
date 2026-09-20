"""
Modulo de carga (Load).
Exporta el DataFrame ya transformado a un archivo Parquet.
"""


def load_data(df, output_path):
    """Guarda el DataFrame transformado en formato Parquet."""
    df.to_parquet(output_path, index=False)
    print(f"Datos exportados a: {output_path}")
