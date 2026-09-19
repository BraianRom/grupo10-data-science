# Ventas cruzadas con datos climáticos — Grupo 10

Proyecto de Ciencia de Datos (metodología **CRISP-DM**) — Opción A.

**Pregunta de investigación:** ¿En qué medida las condiciones meteorológicas diarias explican la variación en la cantidad de unidades vendidas por local, y en qué secciones o categorías se evidencian mayores efectos de ventas cruzadas o sustitución al aislar factores de calendario?

## Estado del proyecto

Fase 1 (Comprensión del problema → Comprensión y preparación de datos → EDA) **en curso**.

## Estructura del repositorio

```
grupo10_data_science/
├── data/
│   ├── raw/          # Datos originales (ventas.csv, metereologia.csv). NO se versionan en Git (ver .gitignore).
│   └── processed/    # df_final.csv/parquet generado por src/preparar_datos.py. NO se versiona si supera el límite de tamaño de Git (ver sección "Datos").
├── notebooks/
│   └── fase1_eda_ventas_clima.ipynb   # EDA completo: univariado, temporal, bivariado, matriz de correlación
├── src/
│   └── preparar_datos.py              # Pipeline de limpieza, melt, imputación, cruce y variables de calendario
├── docs/
│   ├── 01_documento_comprension_problema.pdf
│   ├── 02_informe_fase1_etapas1a5.pdf
│   └── diccionario_datos.xlsx         # Diccionario de datos: fuentes originales + dataset final
├── output/
│   └── fase1_eda_ventas_clima.html    # Exportación HTML del notebook ya ejecutado (generar con el comando de abajo)
├── requirements.txt
└── README.md
```

## Cómo reproducir

1. **Instalar dependencias**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Colocar los datos originales** en `data/raw/`:
   - `data/raw/ventas.csv`
   - `data/raw/metereologia.csv`

   (Los archivos completos no se incluyen en este repositorio por su tamaño — ver sección "Datos" más abajo.)

3. **Generar el dataset final limpio**

   ```bash
   python src/preparar_datos.py
   ```

   Esto crea `data/processed/df_final.csv` (o `.parquet`, ver flag `--formato` dentro del script) aplicando exactamente los pasos documentados en la Etapa 4 del informe (Bitácora de decisiones).

4. **Ejecutar el notebook de EDA**

   Abrir `notebooks/fase1_eda_ventas_clima.ipynb`, ajustar la variable `RUTA_DF_FINAL` para que apunte a `data/processed/df_final.csv`, y ejecutar todas las celdas de principio a fin.

5. **Exportar el notebook a HTML** (requisito del entregable N.° 3)

   ```bash
   jupyter nbconvert --to html --execute notebooks/fase1_eda_ventas_clima.ipynb --output ../output/fase1_eda_ventas_clima.html
   ```

## Datos

El dataset de ventas tiene ~9,4 millones de registros. Por su tamaño, **no se sube el CSV crudo ni el dataset final completo al repositorio de Git** (ver `.gitignore`); en su lugar:

- Se documenta el diccionario de datos completo en `docs/diccionario_datos.xlsx`.
- El dataset limpio resultante (entregable N.° 5) se comparte por el medio que indique la cátedra (enlace a Drive/almacenamiento compartido) o, si el tamaño lo permite tras comprimir/particionar en `.parquet`, se sube con `git lfs`.

## Entregables de la Fase 1 (checklist)

| N.° | Entregable | Ubicación en este repo |
| --- | --- | --- |
| 1 | Documento de comprensión del problema (PDF, 2–3 páginas) | `docs/01_documento_comprension_problema.pdf` |
| 2 | Informe de la Fase 1 (PDF, etapas 1 a 5 + conclusión) | `docs/02_informe_fase1_etapas1a5.pdf` |
| 3 | Notebook ejecutado + exportación HTML | `notebooks/fase1_eda_ventas_clima.ipynb` + `output/fase1_eda_ventas_clima.html` |
| 4 | Diccionario de datos (original y final) | `docs/diccionario_datos.xlsx` |
| 5 | Dataset limpio (.csv/.parquet) | `data/processed/df_final.csv` (generado localmente, ver sección "Datos") |
| 6 | Repositorio Git con README, dependencias y estructura | Este repositorio |

## Autores

Grupo 10 — Ciencia de Datos.
