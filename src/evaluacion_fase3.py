# Fase 3 - Parte 3: evaluacion final sobre el conjunto de prueba.
#
# Este modulo concentra toda la logica de la evaluacion reservada para que el
# notebook quede legible y para que el procedimiento sea reproducible: se ejecuta
# una sola vez sobre 'particion == test' y no debe usarse para reajustar nada.
#
# Entradas  : data/panel_modelado.parquet, output/config_fase3.json,
#             output/modelo_random_forest.joblib
# Salidas   : output/metricas_fase3_test.csv, output/resultados_fase3_test.json,
#             output/predicciones_fase3_test.csv, output/errores_por_segmento_fase3.csv,
#             output/importancia_variables_fase3.csv, output/peores_predicciones_fase3.csv,
#             output/test_real_vs_predicho.png, output/test_residuos_vs_prediccion.png

from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance

SEMILLA = 42

# Las mismas variables con las que se entreno en la Parte 2, en el mismo orden.
VARS_NUMERICAS = ["temperatura", "lag_1", "lag_7", "lag_14",
                  "media_movil_7", "media_movil_28", "mes"]
VARS_CATEGORICAS = ["local", "desc_secciones", "dia_semana"]
VARS_BINARIAS = ["es_fin_de_semana", "es_feriado", "es_quincena", "es_fin_de_mes"]
VARIABLES = VARS_NUMERICAS + VARS_CATEGORICAS + VARS_BINARIAS

OBJETIVO = "cantidad"


def _importar_metricas(ruta_base):
    """Reutiliza metricas_fase3.py de la Parte 1 en lugar de duplicar formulas."""
    ruta_src = str(Path(ruta_base) / "src")
    if ruta_src not in sys.path:
        sys.path.insert(0, ruta_src)
    from metricas_fase3 import metricas
    return metricas


def _linea_base_media(train, test):
    """Base 1: media de unidades por local x seccion calculada SOLO con train."""
    medias = train.groupby(["local", "desc_secciones"])[OBJETIVO].mean()
    idx = pd.MultiIndex.from_frame(test[["local", "desc_secciones"]])
    return medias.reindex(idx).to_numpy()


def _graficar(test, ruta_salida):
    """Dos graficos de diagnostico: ajuste y estructura de los residuos."""
    real = test[OBJETIVO].to_numpy()
    pred = test["pred_random_forest"].to_numpy()

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.scatter(real, pred, s=18, alpha=0.5, edgecolor="none")
    tope = float(max(real.max(), pred.max())) * 1.05
    ax.plot([0, tope], [0, tope], linestyle="--", linewidth=1, color="0.4")
    ax.set_xlabel("Unidades reales")
    ax.set_ylabel("Unidades predichas")
    ax.set_title("Test: valores reales frente a predichos (Random Forest)")
    ax.set_xlim(0, tope)
    ax.set_ylim(0, tope)
    fig.tight_layout()
    fig.savefig(ruta_salida / "test_real_vs_predicho.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.scatter(pred, test["residuo_rf"], s=18, alpha=0.5, edgecolor="none")
    ax.axhline(0, linestyle="--", linewidth=1, color="0.4")
    ax.set_xlabel("Unidades predichas")
    ax.set_ylabel("Residuo (real - predicho)")
    ax.set_title("Test: residuos frente a la prediccion")
    fig.tight_layout()
    fig.savefig(ruta_salida / "test_residuos_vs_prediccion.png", dpi=150)
    plt.close(fig)


def _graficar_importancia(importancia, ruta_salida):
    datos = importancia.sort_values("incremento_rmse_medio")
    fig, ax = plt.subplots(figsize=(7, 5.2))
    ax.barh(datos["variable"], datos["incremento_rmse_medio"],
            xerr=datos["desvio_std"], color="#4878A8", ecolor="0.5", capsize=2)
    ax.axvline(0, linewidth=1, color="0.3")
    ax.set_xlabel("Aumento del RMSE al permutar la variable")
    ax.set_title("Importancia por permutacion sobre el conjunto de prueba")
    fig.tight_layout()
    fig.savefig(ruta_salida / "importancia_variables_fase3.png", dpi=150)
    plt.close(fig)


def ejecutar_evaluacion(ruta_base, n_repeats=20, guardar=True):
    """Evalua el modelo campeon sobre el test reservado y devuelve los resultados.

    Parametros
    ----------
    ruta_base : str o Path
        Raiz del repositorio.
    n_repeats : int
        Repeticiones de la importancia por permutacion.
    guardar : bool
        Si es False no escribe archivos (util para inspeccionar sin sobrescribir).
    """
    ruta_base = Path(ruta_base)
    ruta_salida = ruta_base / "output"
    ruta_salida.mkdir(exist_ok=True)

    metricas = _importar_metricas(ruta_base)
    rng = np.random.RandomState(SEMILLA)

    panel = pd.read_parquet(ruta_base / "data" / "panel_modelado.parquet")
    with open(ruta_salida / "config_fase3.json", encoding="utf-8") as f:
        config = json.load(f)

    train = panel[panel["particion"] == "train"].copy()
    # Se conserva el orden original del panel (cada serie local x seccion
    # contigua y ordenada por fecha); no se reordena para no alterar el
    # muestreo de la importancia por permutacion.
    test = panel[panel["particion"] == "test"].copy().reset_index(drop=True)

    modelo = joblib.load(ruta_salida / "modelo_random_forest.joblib")

    # --- Predicciones: dos lineas base y el modelo campeon --------------------
    test["pred_media"] = _linea_base_media(train, test)
    test["pred_lag7"] = test["lag_7"].to_numpy()
    test["pred_random_forest"] = modelo.predict(test[VARIABLES])
    # Residuo = valor real menos prediccion: negativo significa que el modelo
    # sobreestimo ese dia.
    test["residuo_rf"] = test[OBJETIVO] - test["pred_random_forest"]
    test["error_absoluto_rf"] = test["residuo_rf"].abs()

    filas = [
        metricas(test[OBJETIVO], test["pred_media"], "Base 1 — media por local × sección"),
        metricas(test[OBJETIVO], test["pred_lag7"], "Base 2 — ingenua estacional (lag-7)"),
        metricas(test[OBJETIVO], test["pred_random_forest"], "Random Forest — modelo campeón"),
    ]
    # Se arma la tabla sin redondear: el informe necesita la precision completa.
    tabla = pd.DataFrame(filas).rename(columns={"modelo": "Modelo"})

    rmse_lag7 = float(tabla.loc[tabla["Modelo"].str.contains("lag-7"), "RMSE"].iloc[0])
    mae_lag7 = float(tabla.loc[tabla["Modelo"].str.contains("lag-7"), "MAE"].iloc[0])
    rmse_rf = float(tabla.loc[tabla["Modelo"].str.contains("campeón"), "RMSE"].iloc[0])
    mae_rf = float(tabla.loc[tabla["Modelo"].str.contains("campeón"), "MAE"].iloc[0])

    # --- Error por segmento ---------------------------------------------------
    segmentos = (test.groupby(["local", "desc_secciones"])
                 .apply(lambda d: pd.Series({
                     "n": len(d),
                     "RMSE": float(np.sqrt(np.mean(d["residuo_rf"] ** 2))),
                     "MAE": float(d["error_absoluto_rf"].mean()),
                     "sesgo_medio": float(d["residuo_rf"].mean()),
                 }), include_groups=False)
                 .reset_index())
    segmentos["n"] = segmentos["n"].astype(int)

    # --- Importancia por permutacion -----------------------------------------
    # Mide cuanto empeora el RMSE al romper la relacion de cada variable con el
    # objetivo. Es importancia predictiva, no causal.
    perm = permutation_importance(
        modelo, test[VARIABLES], test[OBJETIVO],
        n_repeats=n_repeats, random_state=SEMILLA,
        scoring="neg_root_mean_squared_error", n_jobs=1,
    )
    importancia = (pd.DataFrame({
        "variable": VARIABLES,
        "incremento_rmse_medio": perm.importances_mean,
        "desvio_std": perm.importances_std,
    }).sort_values("incremento_rmse_medio", ascending=False).reset_index(drop=True))

    peores = test.nlargest(20, "error_absoluto_rf")[[
        "fecha_vta", "local", "desc_secciones", OBJETIVO,
        "pred_random_forest", "residuo_rf", "error_absoluto_rf"]]

    columnas_pred = ["fecha_vta", "local", "desc_secciones", OBJETIVO,
                     "pred_media", "pred_lag7", "pred_random_forest",
                     "residuo_rf", "error_absoluto_rf"]

    resumen = {
        "modelo_campeon": "Random Forest Regressor",
        "fecha_inicio_test": str(pd.to_datetime(test["fecha_vta"]).min().date()),
        "fecha_fin_test": str(pd.to_datetime(test["fecha_vta"]).max().date()),
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "metricas_test": json.loads(tabla.to_json(orient="records", force_ascii=False)),
        "reduccion_rmse_vs_lag7_pct": (rmse_lag7 - rmse_rf) / rmse_lag7 * 100,
        "reduccion_mae_vs_lag7_pct": (mae_lag7 - mae_rf) / mae_lag7 * 100,
        "residuo_medio": float(test["residuo_rf"].mean()),
        "residuo_mediano": float(test["residuo_rf"].median()),
        "nota_importancia": "Importancia predictiva por permutación; no implica causalidad.",
        "peores_casos_exportados": int(len(peores)),
        "advertencia": "El conjunto test se evalúa una sola vez; no debe usarse para reajustar el modelo.",
    }

    if guardar:
        tabla.to_csv(ruta_salida / "metricas_fase3_test.csv", index=False, encoding="utf-8-sig")
        test[columnas_pred].to_csv(ruta_salida / "predicciones_fase3_test.csv",
                                   index=False, encoding="utf-8-sig")
        segmentos.to_csv(ruta_salida / "errores_por_segmento_fase3.csv",
                         index=False, encoding="utf-8-sig")
        importancia.to_csv(ruta_salida / "importancia_variables_fase3.csv",
                           index=False, encoding="utf-8-sig")
        peores.to_csv(ruta_salida / "peores_predicciones_fase3.csv",
                      index=False, encoding="utf-8-sig")
        with open(ruta_salida / "resultados_fase3_test.json", "w", encoding="utf-8") as f:
            json.dump(resumen, f, ensure_ascii=False, indent=2)
        _graficar(test, ruta_salida)
        _graficar_importancia(importancia, ruta_salida)

    return {
        "metricas": tabla,
        "predicciones": test[columnas_pred],
        "segmentos": segmentos,
        "importancia": importancia,
        "peores": peores,
        "resumen": resumen,
        "config": config,
    }
