"""
Modulo de transformacion (Transform).
Limpia el dataset y agrega una columna calculada propia
(posiciones ganadas o perdidas respecto a la largada).
"""

import re


def normalizar_nombres_columnas(df):
    """
    Ya vienen en snake_case desde la extraccion, pero se deja esta funcion
    por si el dia de manana cambia la fuente de datos y trae columnas con
    otro formato (espacios, mayusculas, etc.).
    """
    nuevas_columnas = {c: re.sub(r"\s+", "_", c.strip().lower()) for c in df.columns}
    return df.rename(columns=nuevas_columnas)


def eliminar_duplicados(df):
    """Elimina filas exactamente iguales (por ejemplo, si la API devuelve la misma carrera dos veces)."""
    antes = len(df)
    df = df.drop_duplicates()
    print(f"Duplicados eliminados: {antes - len(df)}")
    return df


def manejar_nulos(df):
    """
    - points: no deberia tener nulos (la API devuelve 0 si no sumo puntos),
      pero por las dudas se completa con 0.
    - grid: entero chico, casi nunca nulo; si aparece, se completa con la
      mediana.
    - position: SI puede quedar nulo cuando el piloto abandono la carrera
      y no llego a clasificar. Ese nulo no es un dato que falte por error,
      es un "no aplica": no tiene una posicion de llegada real. Por eso NO
      se inventa un numero ahi. En cambio, se dejan esos nulos como estan
      y se agrega una columna booleana 'no_clasifico' para que la
      ausencia de dato quede visible y explicita, en vez de escondida.
    """
    df["points"] = df["points"].fillna(0)
    df["grid"] = df["grid"].fillna(df["grid"].median())

    df["no_clasifico"] = df["position"].isnull()

    return df


def calcular_posiciones_ganadas(df):
    """
    Funcion propia (no es limpieza, es una columna nueva calculada).

    Compara la posicion de largada (grid) con la de llegada (position)
    para saber cuantos lugares gano o perdio el piloto durante la carrera.
    Ejemplo: largo 15 y termino 8 -> gano 7 posiciones (+7).

    Si el piloto no clasifico (no_clasifico = True), el calculo queda en
    nulo a proposito: no tiene sentido decir que "gano 0 posiciones" si en
    realidad no llego a la bandera a cuadros, seria un dato enganoso.
    """
    df["posiciones_ganadas"] = df["grid"] - df["position"]
    return df


def transform_data(df):
    """Orquesta las etapas de limpieza y el agregado de la columna propia, en orden."""
    df = normalizar_nombres_columnas(df)
    df = eliminar_duplicados(df)
    df = manejar_nulos(df)
    df = calcular_posiciones_ganadas(df)
    print("Transformacion completada")
    return df
