# Metricas compartidas del proyecto - Fase 3. Generado por la Parte 1.
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def metricas(y_true, y_pred, nombre="modelo"):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    valido = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true, y_pred = y_true[valido], y_pred[valido]
    no_cero = y_true != 0
    mape = (float(np.mean(np.abs((y_true[no_cero] - y_pred[no_cero]) / y_true[no_cero])) * 100)
            if no_cero.any() else np.nan)
    return {
        "modelo": nombre,
        "n": int(len(y_true)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "MAPE_%": mape,
        "R2": float(r2_score(y_true, y_pred)),
        "filas_excluidas_MAPE": int((~no_cero).sum()),
    }


def tabla_metricas(lista_resultados):
    return pd.DataFrame(lista_resultados).set_index("modelo").round(4)
