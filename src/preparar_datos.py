"""
Pipeline de preparación de datos — Fase 1 CRISP-DM
Proyecto: Ventas cruzadas con datos climáticos (Grupo 10)

Este script reproduce, paso a paso, las decisiones documentadas en la
Etapa 4 del informe (Bitácora de decisiones - Preparación de los datos):

  1. Limpieza de caracteres no numéricos (asteriscos) en la matriz de temperatura.
  2. Reestructuración (melt) del dataset meteorológico de formato ancho a largo.
  3. Eliminación de nulos estructurales (fechas inexistentes, ej. 30 de febrero).
  4. Imputación de temperatura por interpolación lineal (con la media de la
     estación como respaldo en los extremos de la serie).
  5. Conversión de fecha_vta a datetime64.
  6. Asignación de cada local a una estación meteorológica (mapeo manual).
  7. Cruce (merge) de ventas y clima por fecha y estación asignada.
  8. Agregado de variables de calendario (día de semana, fin de semana,
     mes, año, feriado en Paraguay).

IMPORTANTE:
- Este script asume que 'ventas.csv' y 'metereologia.csv' ya están en
  data/raw/. Esos archivos NO se incluyen en el repositorio por su tamaño.
- El mapeo local -> estación (MAPEO_LOCAL_ESTACION) es un supuesto
  simplificador, tal como se documenta en el informe: el dataset de
  ventas no incluye coordenadas reales de los locales. Ajustar este
  diccionario a la asignación real usada por el grupo antes de ejecutar.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import holidays
except ImportError:  # pragma: no cover
    holidays = None


# ------------------------------------------------------------------
# Configuración de rutas
# ------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
RUTA_VENTAS = RAIZ / "data" / "raw" / "ventas.csv"
RUTA_METEO = RAIZ / "data" / "raw" / "metereologia.csv"
RUTA_SALIDA_CSV = RAIZ / "data" / "processed" / "df_final.csv"
RUTA_SALIDA_PARQUET = RAIZ / "data" / "processed" / "df_final.parquet"

# ------------------------------------------------------------------
# Mapeo local -> estación meteorológica (AJUSTAR según la asignación real
# documentada por el grupo; este es un valor de ejemplo / placeholder).
# ------------------------------------------------------------------
MAPEO_LOCAL_ESTACION = {
    # "Local 01": "Asunción, Silvio Pettirossi",
    # "Local 02": "Ciudad del Este",
    # "Local 03": "Encarnación",
}


def cargar_ventas(ruta: Path) -> pd.DataFrame:
    """Carga el dataset de ventas y convierte fecha_vta a datetime64 (paso 5)."""
    df_ventas = pd.read_csv(ruta, dtype={"local": "category"}, low_memory=False)
    df_ventas["fecha_vta"] = pd.to_datetime(df_ventas["fecha_vta"], errors="coerce")
    return df_ventas


def limpiar_y_reestructurar_meteorologia(ruta: Path) -> pd.DataFrame:
    """Aplica los pasos 1 a 4 sobre el dataset meteorológico (formato ancho -> largo)."""
    df_meteo = pd.read_csv(ruta, low_memory=False)

    columnas_dia = [c for c in df_meteo.columns if c.lower().startswith("día") or c.lower().startswith("dia")]

    # Paso 1: limpieza de caracteres no numéricos (asteriscos -> NaN)
    for col in columnas_dia:
        df_meteo[col] = (
            df_meteo[col]
            .astype(str)
            .str.replace("*", "", regex=False)
            .replace({"nan": np.nan, "": np.nan})
        )
        df_meteo[col] = pd.to_numeric(df_meteo[col], errors="coerce")

    # Paso 2: reestructuración (melt) de formato ancho a formato largo
    id_vars = [c for c in df_meteo.columns if c not in columnas_dia]
    df_largo = df_meteo.melt(
        id_vars=id_vars, value_vars=columnas_dia, var_name="dia_col", value_name="temperatura"
    )
    df_largo["dia"] = df_largo["dia_col"].str.extract(r"(\d+)").astype(int)

    col_anio = "Año" if "Año" in df_largo.columns else "anio"
    col_mes = "Mes" if "Mes" in df_largo.columns else "mes"

    df_largo["fecha"] = pd.to_datetime(
        dict(year=df_largo[col_anio], month=df_largo[col_mes], day=df_largo["dia"]),
        errors="coerce",
    )

    # Paso 3: eliminación de nulos estructurales (fechas inexistentes, ej. 30 de febrero)
    n_antes = len(df_largo)
    df_largo = df_largo.dropna(subset=["fecha"]).copy()
    n_despues = len(df_largo)
    print(f"[preparar_datos] Nulos estructurales eliminados (fechas inexistentes): {n_antes - n_despues}")

    # Paso 4: imputación de temperatura por interpolación lineal dentro de cada
    # estación, con la media de la estación como respaldo en los extremos.
    df_largo = df_largo.sort_values(["Estación", "fecha"])
    df_largo["temperatura"] = df_largo.groupby("Estación", observed=True)["temperatura"].transform(
        lambda s: s.interpolate(method="linear", limit_direction="both")
    )
    media_por_estacion = df_largo.groupby("Estación", observed=True)["temperatura"].transform("mean")
    df_largo["temperatura"] = df_largo["temperatura"].fillna(media_por_estacion)

    columnas_finales = ["Estación", "fecha", "temperatura"]
    if "Código" in df_largo.columns:
        columnas_finales.insert(1, "Código")

    return df_largo[columnas_finales].reset_index(drop=True)


def asignar_estacion(df_ventas: pd.DataFrame, mapeo: dict) -> pd.DataFrame:
    """Paso 6: asigna cada local a una estación meteorológica mediante mapeo manual."""
    if not mapeo:
        raise ValueError(
            "MAPEO_LOCAL_ESTACION está vacío. Completá el diccionario en la parte "
            "superior de este script con la asignación real local -> estación "
            "antes de ejecutar el pipeline."
        )
    df_ventas = df_ventas.copy()
    df_ventas["estacion_asignada"] = df_ventas["local"].astype(str).map(mapeo)

    sin_asignar = df_ventas["estacion_asignada"].isna().sum()
    if sin_asignar > 0:
        locales_faltantes = sorted(df_ventas.loc[df_ventas["estacion_asignada"].isna(), "local"].unique())
        print(
            f"[preparar_datos] ADVERTENCIA: {sin_asignar} registros sin estación asignada. "
            f"Locales faltantes en el mapeo: {locales_faltantes}"
        )
    return df_ventas


def agregar_variables_calendario(df: pd.DataFrame, col_fecha: str = "fecha_vta") -> pd.DataFrame:
    """Paso 8: agrega día de semana, fin de semana, mes, año y feriado (Paraguay)."""
    df = df.copy()
    df["dia_semana"] = df[col_fecha].dt.dayofweek  # 0 = lunes
    df["es_fin_de_semana"] = df["dia_semana"].isin([5, 6]).astype(int)
    df["mes"] = df[col_fecha].dt.month
    df["anio"] = df[col_fecha].dt.year

    if holidays is not None:
        anios = sorted(df["anio"].dropna().unique().tolist())
        feriados_py = holidays.Paraguay(years=anios)
        df["es_feriado"] = df[col_fecha].dt.date.isin(feriados_py).astype(int)
    else:
        print("[preparar_datos] ADVERTENCIA: paquete 'holidays' no disponible; es_feriado se completa con 0.")
        df["es_feriado"] = 0

    return df


def construir_df_final(mapeo_local_estacion: dict = MAPEO_LOCAL_ESTACION) -> pd.DataFrame:
    print("[preparar_datos] Cargando ventas...")
    df_ventas = cargar_ventas(RUTA_VENTAS)

    print("[preparar_datos] Limpiando y reestructurando meteorología...")
    df_meteo_largo = limpiar_y_reestructurar_meteorologia(RUTA_METEO)

    print("[preparar_datos] Asignando estación meteorológica a cada local...")
    df_ventas = asignar_estacion(df_ventas, mapeo_local_estacion)

    print("[preparar_datos] Agregando variables de calendario...")
    df_ventas = agregar_variables_calendario(df_ventas, col_fecha="fecha_vta")

    print("[preparar_datos] Cruzando (merge) ventas y clima por fecha y estación...")
    n_antes = len(df_ventas)
    df_final = df_ventas.merge(
        df_meteo_largo,
        left_on=["fecha_vta", "estacion_asignada"],
        right_on=["fecha", "Estación"],
        how="left",
    )
    n_despues = len(df_final)
    sin_temperatura = df_final["temperatura"].isna().sum()

    print(f"[preparar_datos] Registros antes del cruce: {n_antes:,} | después: {n_despues:,}")
    print(f"[preparar_datos] Filas sin temperatura asignada tras el merge: {sin_temperatura:,}")

    if n_antes != n_despues:
        print(
            "[preparar_datos] ADVERTENCIA: la cantidad de filas cambió tras el merge "
            "(posible duplicación). Revisar unicidad de (fecha, estación) en el "
            "dataset meteorológico."
        )

    return df_final


def main():
    parser = argparse.ArgumentParser(description="Pipeline de preparación de datos - Fase 1")
    parser.add_argument(
        "--formato", choices=["csv", "parquet", "ambos"], default="csv",
        help="Formato de salida del dataset final (default: csv)",
    )
    args = parser.parse_args()

    RUTA_SALIDA_CSV.parent.mkdir(parents=True, exist_ok=True)

    df_final = construir_df_final()

    if args.formato in ("csv", "ambos"):
        df_final.to_csv(RUTA_SALIDA_CSV, index=False)
        print(f"[preparar_datos] Dataset final guardado en: {RUTA_SALIDA_CSV}")
    if args.formato in ("parquet", "ambos"):
        df_final.to_parquet(RUTA_SALIDA_PARQUET, index=False)
        print(f"[preparar_datos] Dataset final guardado en: {RUTA_SALIDA_PARQUET}")


if __name__ == "__main__":
    main()
