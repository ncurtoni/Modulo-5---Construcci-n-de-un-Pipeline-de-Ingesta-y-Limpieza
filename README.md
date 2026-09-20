# etl-pipeline

Pipeline de datos que extrae, transforma y carga (ETL) el historial de
resultados de carrera de Franco Colapinto desde la API Jolpica-F1, optimizando
tipos de datos y exportando el resultado a formato Parquet.

Flujo: API Jolpica-F1 -> **Extract** -> DataFrame -> **Transform** -> datos
limpios + columna calculada propia -> **Load** -> `dataset_procesado.parquet`

## Estructura del proyecto

```
etl-pipeline/
├── data/
│   ├── raw/            (el csv crudo se genera aca al correr el pipeline, no se sube al repo)
│   └── processed/      (el parquet resultante se genera aca, no se sube al repo)
├── src/
│   ├── __init__.py
│   ├── extract.py      # Etapa de extraccion (API) y optimizacion de tipos
│   ├── transform.py     # Etapa de limpieza + funcion propia (posiciones ganadas)
│   └── load.py          # Etapa de carga a Parquet
├── .gitignore
├── main.py               # Orquestador: corre las 3 etapas + validacion
├── README.md
└── requirements.txt
```

## Dataset

A diferencia de un CSV descargado de antemano, este pipeline extrae los datos
en el momento desde una API publica: [Jolpica-F1](https://github.com/jolpica/jolpica-f1)
, consultando el historial de resultados de carrera de
Franco Colapinto. No hace falta descargar nada a mano: el propio script pide
los datos y genera `data/raw/dataset.csv` como una copia cruda antes de
limpiarlo.

## Como instalar y ejecutar

Este proyecto se corre sin instalar nada en la computadora, usando Google
Colab:

1. Subir la carpeta `etl-pipeline` completa a Colab (o clonar el repo con
   `!git clone <url-del-repo>` en una celda).
2. Instalar las dependencias:
   ```
   !pip install -r requirements.txt
   ```
3. Ejecutar el pipeline:
   ```
   !python main.py
   ```

Si se prefiere correrlo localmente con Python instalado, los pasos son los
mismos, parado con la terminal dentro de la carpeta `etl-pipeline`:

```bash
pip install -r requirements.txt
python main.py
```

Una ejecucion correcta muestra las cuatro etapas (Extraccion, Transformacion,
Carga, Validacion) y termina con "Pipeline ejecutado con exito."

## Que hace cada etapa

### 1. Extraccion (`src/extract.py`)

- Pide a `/drivers/colapinto/results.json` el historial completo de carreras.
- Guarda una copia cruda, (una tabla plana), en `data/raw/dataset.csv` (esto permite
  comparar después el antes y el despues, en la etapa de validación).
- Optimiza los tipos de datos sobre una copia en memoria:
  - `season`, `round`, `grid`: simplifica a enteros chicos.
  - `position`: se convierte a `Int64` (con mayuscula), el tipo entero de
    pandas que admite nulos. Un `int` comun no puede tener `NaN`, y esta
    columna si puede quedar vacia (ver mas abajo).
  - `points`: simplifica a `float32`.
  - `constructor`, `status`: a `category` (pocos valores distintos que se
    repiten en cada fila).

### 2. Transformacion (`src/transform.py`)

- Normaliza los nombres de columna.
- Elimina filas duplicadas.
- Maneja los nulos de forma distinta segun la columna:
  - `points`, `grid`: se completan (con 0 y con la mediana respectivamente)
    si llegaran a faltar.
  - `position`: puede quedar vacio si el piloto abandono la carrera (no
    llego a clasificar). Ese vacio **no se completa con un numero
    inventado**, porque no es un dato faltante por error, es un "no
    aplica". En cambio, se agrega una columna booleana `no_clasifico` para
    dejarlo explicito.
- **Funcion propia**: `calcular_posiciones_ganadas`, que resta la posicion
  de llegada a la de largada (`grid - position`) para saber cuantos lugares
  gano o perdio el piloto durante la carrera. Si no clasifico, esta columna
  tambien queda en nulo a proposito (no tendria sentido decir que "gano 0
  posiciones" si en realidad no termino la carrera).

### 3. Carga (`src/load.py`)

Exporta el DataFrame limpio a `data/processed/dataset_procesado.parquet`.

### 4. Validacion (`main.py`, funcion `validar_raw_vs_procesado`)

Antes de dar el pipeline por terminado, se vuelve a leer el csv crudo
(`data/raw/dataset.csv`) y el parquet procesado, y se comparan:

- Cantidad de filas y columnas (el procesado tiene 2 columnas mas: las
  agregadas en la transformacion).
- Cantidad de duplicados en cada uno.
- Nulos en `points` antes y despues.
- Tipos de datos de `season` y `constructor` antes y despues (para
  confirmar que la optimizacion de tipos realmente se aplico, no solo
  asumirlo).

## Por que Parquet y no CSV

CSV es texto plano: facil de intercambiar, pero no guarda el tipo de dato de
cada columna (todo se relee como texto hasta que algo lo interpreta de
nuevo) y no comprime. Parquet es un formato binario columnar que preserva
los tipos optimizados en la extraccion, comprime el archivo, y es mas rapido
de leer para un pipeline de Machine Learning posterior, porque permite leer
columnas especificas sin procesar el archivo entero. Y es pedido en la consigna

## Sobre el .gitignore

```
venv/
__pycache__/
*.pyc

data/raw/*.csv
data/processed/*.parquet
```

El csv crudo y el parquet procesado se generan cada vez que se corre el
pipeline, asi que no hace falta (ni conviene) subirlos al repositorio. Las
carpetas `data/raw/` y `data/processed/` se mantienen visibles gracias a un
archivo `.gitkeep` vacio en cada una.
