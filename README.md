# Grupo 10 — Impacto del clima sobre las ventas de un comercio minorista

Proyecto integrador de la asignatura **Data Science (electiva)** — Universidad Nacional de Asunción,
Facultad Politécnica, Ingeniería Informática. Metodología **CRISP-DM**, desarrollada en tres fases
acumulativas sobre el mismo conjunto de datos.

---

## 1. Problema y objetivos

Un comercio minorista con dos locales quiere saber si las condiciones meteorológicas explican la
variación de sus ventas diarias y si conviene incorporarlas a la planificación de reposición. La
intuición del negocio es que el calor desplaza el consumo entre categorías: más bebidas, menos
perecederos. El proyecto pone esa intuición a prueba y, además, evalúa si el clima aporta capacidad
predictiva por encima de lo que ya aporta el propio historial de ventas.

**Pregunta de investigación.** ¿En qué medida las condiciones meteorológicas diarias explican la
variación en la cantidad de unidades vendidas por local, y en qué secciones se evidencian efectos de
sustitución al aislar los factores de calendario?

**Objetivo general.** Analizar el efecto de las variables meteorológicas sobre el volumen de unidades
vendidas a nivel de local y sección, aislando los factores de calendario.

**Objetivos específicos.**

1. Integrar dos fuentes heterogéneas en un único conjunto analizable y documentar cada transformación.
2. Contrastar formalmente cinco hipótesis sobre el efecto del clima, distinguiendo significancia
   estadística de relevancia práctica.
3. Construir un modelo predictivo de unidades vendidas por día, local y sección, y medir si supera a
   una línea base ingenua.
4. Determinar el peso real de la temperatura dentro del modelo final.

---

## 2. Integrantes

| Nombre | Usuario de GitHub | Responsabilidad principal |
|---|---|---|
| Leyda Fleitas | `leydafleitas` | Fase 1 (preparación e integración de datos) · Fase 2 (hipótesis H1 y H2) · Fase 3 Parte 1 (diseño del experimento y líneas base) |
| Ryuto Maehara | `rmae-5` / `mryuto` | Fase 1 (análisis exploratorio) · Fase 2 (hipótesis H3 a H5 e informe) · Fase 3 Parte 2 (modelado y validación cruzada) |
| Braian Romero | `BraianRom` | Fase 3 Parte 3 (evaluación final, análisis de errores e interpretabilidad) |

---

## 3. Datos y su fuente

Los dos archivos originales fueron provistos por la cátedra y corresponden a un comercio minorista real
anonimizado (los locales figuran como `Local X` y `Local Y`). No contienen identificación de clientes,
por lo que no constituyen datos personales.

| Archivo | Contenido | Cobertura real | Tamaño |
|---|---|---|---|
| `ventas.csv` | 9.447.662 registros transaccionales (ítem × sucursal × fecha) | 271 días, enero a septiembre de 2021 | ~917 MB |
| `metereologia.csv` | Temperatura diaria por estación meteorológica, en formato ancho | 660 filas = 20 estaciones × 33 meses (enero 2019 – septiembre 2021) | ~60 KB |

### Nota sobre la cobertura temporal

El perfilado inicial de la Fase 1 declaraba "3 años continuos (2019–2021)" y "36 meses" de datos
meteorológicos. Al construir la serie diaria agregada se detectó que la cobertura real es menor y se
verificó el origen de la diferencia: el archivo meteorológico cubre 33 meses y el de ventas solo 271 días
de 2021. El cruce entre ambas fuentes no produjo pérdida de registros (9.447.662 antes y después del
`merge`, con 0 filas sin temperatura asignada), de modo que la diferencia proviene de la cobertura del
archivo de ventas y no del proceso de preparación. La documentación de la Fase 1 fue corregida en
consecuencia. **Toda conclusión del proyecto vale para enero–septiembre de 2021 y no para un ciclo
estacional completo.**

### Unidades de análisis por fase

| Fase | Unidad | Observaciones |
|---|---|---|
| Fase 1 | Transacción (ítem × sucursal × fecha) | 9.447.662 |
| Fase 2 | Según la hipótesis: serie diaria, panel fecha × local × sección, o transacción | 271 a 427.689 |
| Fase 3 | Panel fecha × local × sección | 3.429 filas utilizables (2 locales × 9 secciones) |

### Archivos no versionados

Por su tamaño, los datos originales y el dataset integrado no se incluyen en el repositorio:

| Archivo | Tamaño | Cómo obtenerlo |
|---|---|---|
| `ventas.csv` | ~917 MB | Fuente provista por la cátedra |
| `df_final.parquet` | ~70 MB | Se regenera ejecutando los notebooks de la Fase 1 |

El panel de modelado derivado (`data/panel_modelado.parquet`, ~150 KB) **sí** está versionado, porque es
liviano y es la entrada directa de la Fase 3. Esto permite reproducir las Fases 3.2 y 3.3 sin descargar
los archivos originales.

---

## 4. Tecnologías

| Herramienta | Uso |
|---|---|
| Python 3.10+ | Lenguaje base |
| pandas, numpy | Manipulación y reestructuración de datos |
| pyarrow | Lectura y escritura de archivos `.parquet` |
| matplotlib, seaborn | Visualizaciones |
| scipy, statsmodels | Pruebas de hipótesis, OLS, errores robustos y agrupados |
| scikit-learn | Modelado predictivo, validación cruzada temporal, importancia por permutación |
| joblib | Serialización de los modelos entrenados |
| holidays | Feriados de Paraguay para las variables de calendario |
| Google Colab / Jupyter | Entorno de ejecución |

---

## 5. Estructura del repositorio

```
.
├── data/
│   └── panel_modelado.parquet        Panel de la Fase 3 (entrada directa del modelado)
├── docs/                             Informes y diccionario de datos
├── notebooks/                        Notebooks de las tres fases
├── output/                           Artefactos: configuración, métricas, modelos, gráficos
├── src/                              Código reutilizable entre fases
├── requirements.txt
└── README.md
```

La Fase 2 aporta dos notebooks: `fase2-Completo.ipynb` contiene las cinco hipótesis y es el que
corresponde a la entrega de la fase, mientras que `fase2.ipynb` conserva únicamente los contrastes H1 y
H2 tal como se desarrollaron por separado antes de integrarlos.

---

## 6. Instrucciones de ejecución

### Requisitos

```bash
pip install -r requirements.txt
```

En Google Colab, cada notebook define al inicio una variable de ruta que debe apuntar a la raíz del
proyecto montada en Drive:

```python
RUTA_BASE = "/content/drive/MyDrive/grupo10_data_science"
```

Ejecutado localmente desde una copia del repositorio, los notebooks de la Fase 3 detectan la raíz
automáticamente.

### Orden de ejecución

Los notebooks deben ejecutarse **en orden**, porque cada uno consume artefactos generados por el anterior.

#### Fase 1 — Comprensión, preparación y análisis exploratorio

```
notebooks/fase1.ipynb                 (limpieza, integración y variables de calendario)
notebooks/fase1_dataset_final.ipynb   (análisis exploratorio)
```

Limpia los datos meteorológicos (asteriscos a nulos, reestructuración de formato ancho a largo con
`melt`, imputación por interpolación lineal dentro de cada estación), convierte tipos, asigna una
estación meteorológica a cada local, cruza ambas fuentes y agrega las variables de calendario.

**Produce:** `df_final.parquet` — dataset integrado de 9.447.662 registros con clima y calendario.

#### Fase 2 — Análisis inferencial

```
notebooks/fase2-Completo.ipynb
```

Contrasta las cinco hipótesis derivadas del análisis exploratorio, con verificación de supuestos,
intervalos de confianza, tamaños de efecto y corrección por comparaciones múltiples.

**Consume:** `df_final.parquet` · **Produce:** tabla resumen de contrastes y el informe de la fase.

#### Fase 3 — Análisis predictivo

```
notebooks/fase3_parte1_diseno_experimento.ipynb
notebooks/fase3_parte2_modelado.ipynb
notebooks/fase3_parte3_evaluacion.ipynb
```

**Parte 1** define la tarea predictiva, construye el panel, realiza la partición cronológica y establece
las líneas base.
*Consume:* `df_final.parquet` · *Produce:* `data/panel_modelado.parquet`, `output/config_fase3.json`,
`src/metricas_fase3.py`

**Parte 2** entrena y ajusta cuatro familias de modelos sobre `particion == 'train'`, con validación
cruzada temporal de 5 pliegues de 28 días y diagnóstico explícito del sobreajuste.
*Consume:* el panel, la configuración y `src/metricas_fase3.py` · *Produce:* los `.joblib` de cada modelo,
`output/resultados_cv_fase3.json` y `output/comparativa_modelado_train_val.csv`

**Parte 3** evalúa sobre `particion == 'test'` una sola vez, analiza los errores por segmento e
interpreta el modelo por permutación.
*Consume:* el panel y `output/modelo_random_forest.joblib` · *Produce:* `output/metricas_fase3_test.csv`,
`output/resultados_fase3_test.json`, `output/errores_por_segmento_fase3.csv`,
`output/importancia_variables_fase3.csv`, `output/peores_predicciones_fase3.csv`,
`output/predicciones_fase3_test.csv` y los tres gráficos `.png`

La lógica de la Parte 3 vive en `src/evaluacion_fase3.py`, de modo que el notebook se limita a invocarla
y a mostrar los resultados.

### Reproducibilidad

- **Semilla fija:** `SEMILLA = 42` en todas las fases (partición, modelos y permutaciones).
- **Entorno de referencia:** Python 3.10+, pandas ≥ 2.0, scikit-learn ≥ 1.3. Los archivos `.joblib`
  conviene cargarlos con la misma versión de scikit-learn con la que fueron serializados.
- Toda transformación se realiza por código desde los archivos originales; no se edita ningún dato a mano.
- Los notebooks se ejecutan de principio a fin en un entorno limpio y regeneran sus salidas.

---

## 7. Síntesis de resultados

### Fase 1 — Preparación y exploración

Dataset integrado de 9.447.662 registros, sin pérdida ni duplicación en el cruce. Se corrigieron 18
celdas de temperatura con asterisco, se reestructuraron 660 filas en formato ancho a 20.080 registros
diarios válidos y se descartaron 380 fechas inexistentes generadas por la matriz de 31 columnas del
archivo original. El análisis exploratorio identificó una estacionalidad semanal marcada (el sábado vende
un 78 % más que un miércoles) frente a una correlación entre temperatura y ventas diarias de apenas 0,07.
De ahí salieron las cinco hipótesis de la Fase 2.

### Fase 2 — Análisis inferencial

| Hipótesis | Prueba | Resultado |
|---|---|---|
| **H1** — Las ventas de Bebidas difieren por grupo climático | ANOVA de 2 factores + Tukey HSD | Se rechaza H0 (p = 2,7e-13) con tamaño de efecto nulo (η² = 0,0001). Con errores agrupados por fecha, p = 0,18 |
| **H2** — La temperatura se asocia a las ventas totales diarias | OLS con controles de calendario | **No se rechaza H0** (p = 0,254). Coeficiente −131,05, IC 95 % [−356,58; 94,48] |
| **H3** — El efecto del clima difiere entre secciones | Wald F robusto + corrección de Holm | Se rechaza H0 (p = 3,2e-49) con magnitud modesta (−2,2 % a +1,3 % por °C). Solo Tienda, Almacén y Producción resisten la corrección |
| **H4** — El fin de semana modera el efecto climático | OLS con interacción, errores HC3 | **No se rechaza H0** (p = 0,91) |
| **H5** — El efecto climático varía por local | Wald F robusto + bootstrap por bloques | **No se rechaza H0** (p = 0,092). Ninguna de 7 especificaciones rechaza |

En el mismo modelo en que la temperatura no resulta significativa, el fin de semana suma 18.170 unidades
diarias (IC 95 % [16.200; 20.200]) y los feriados 11.030 (IC 95 % [5.916; 16.100]). No es falta de
potencia: el efecto del clima simplemente no está.

**Diagnóstico de confusión.** La variable `mes` explica el 44,2 % de la variación de la temperatura
diaria. Al quitar ese control, el coeficiente de temperatura en H2 pasa de −131,0 a +84,2 y en H5 de
+83,2 a −39,5; en H3 cambian de signo 4 de las 9 secciones. El control por calendario es lo que impide
confundir estacionalidad con efecto climático.

### Fase 3 — Análisis predictivo

Tarea de regresión sobre unidades vendidas por día, local y sección, horizonte t+1. Partición cronológica
con corte el **19 de agosto de 2021**: 2.835 filas de entrenamiento y 594 de prueba.

**Selección del modelo (validación cruzada temporal sobre train):**

| Familia | Modelo | Train RMSE | CV Val RMSE | CV Val R² | Brecha (Val − Tr) |
|---|---|---|---|---|---|
| Línea base | Media por grupo | 1167,4 | 1162,7 ± 169,5 | 0,833 | −4,7 |
| Línea base | Lag-7 estacional | 850,9 | 748,1 ± 421,6 | 0,927 | −102,8 |
| Lineal | Ridge (α = 20) | 657,1 | 618,0 ± 256,5 | 0,952 | −39,1 |
| **Árboles (bagging)** | **Random Forest (n=150, d=16, leaf=2)** | **398,9** | **573,4 ± 271,1** | **0,958** | **+174,5** |
| Árboles (boosting) | HistGradientBoosting (lr=0,03, d=4) | 435,2 | 638,0 ± 250,9 | 0,949 | +202,8 |
| Distancias | KNN (k=7, distance) | 0,0 | 680,0 ± 292,2 | 0,943 | +680,0 |

**Evaluación final sobre el conjunto de prueba (una sola vez):**

| Modelo | RMSE | MAE | MAPE | R² |
|---|---|---|---|---|
| Base 1 — media por local × sección | 1077,2 | 603,8 | 67,4 % | 0,781 |
| Base 2 — ingenua estacional (lag-7) | 700,6 | 318,0 | 39,5 % | 0,907 |
| **Random Forest — modelo campeón** | **547,7** | **239,6** | **37,7 %** | **0,943** |

El modelo campeón mejora a la línea base ingenua en **21,8 % de RMSE** y **24,6 % de MAE**, con un sesgo
medio de −22,6 unidades sobre un nivel medio muy superior, es decir prácticamente insesgado.

**Interpretabilidad (importancia por permutación sobre test, 20 repeticiones):**

| Variable | Aumento del RMSE | % del RMSE del modelo |
|---|---|---|
| `lag_14` | 406,9 | 74 % |
| `media_movil_28` | 263,5 | 48 % |
| `lag_7` | 226,4 | 41 % |
| `media_movil_7` | 183,6 | 34 % |
| `lag_1` | 160,9 | 29 % |
| `desc_secciones` | 73,7 | 13 % |
| `es_feriado` | 0,4 | 0,07 % |
| `mes` | 0,0 | 0 % |
| **`temperatura`** | **−2,5** | **−0,46 %** |

Permutar la temperatura no empeora el modelo. La capacidad predictiva proviene casi por completo del
historial reciente de ventas de cada serie.

### Conclusión integrada

Las dos mitades del proyecto, que usan técnicas con supuestos distintos, llegan al mismo resultado: el
clima no explica una porción relevante de la variación de ventas en el período analizado, y el calendario
y la inercia de la propia serie sí. La hipótesis de sustitución entre categorías que planteaba el negocio
no se sostiene una vez corregido por comparaciones múltiples.

---

## 8. Decisiones metodológicas relevantes

| Decisión | Fundamento |
|---|---|
| Asignación manual de local a estación meteorológica | El dataset no incluye geografía real de los locales. Supuesto simplificador documentado |
| Nulos estructurales eliminados, no imputados | Corresponden a fechas inexistentes (ej. 30 de febrero) generadas por la matriz de 31 columnas |
| Panel reindexado sobre el calendario completo | Garantiza que `lag_7` signifique siete días y no siete filas |
| Celdas sin ventas conservadas como nulas, no como cero | Un día sin registros es un día sin operación del local, no un día de cero ventas |
| Partición cronológica, nunca aleatoria | Entrenar con el futuro para predecir el pasado invalida la evaluación |
| Línea base ingenua estacional, no la media | Con estacionalidad semanal fuerte, la media es una vara demasiado baja: lag-7 ya alcanza R² = 0,907 |
| Corrección de Holm en H3 | Con 9 pruebas simultáneas al 5 %, la probabilidad de al menos un falso positivo es del 37 % |
| Tamaños de efecto junto a los p-valores | Con cientos de miles de observaciones, diferencias triviales resultan significativas |
| Test evaluado una sola vez | Reajustar sobre test convierte la evaluación en ajuste y anula su valor |

---

## 9. Limitaciones

- **Cobertura temporal.** Enero a septiembre de 2021, un único año parcial. No incluye un ciclo estacional
  cerrado, lo que acota el rango de temperaturas observado.
- **Resolución espacial.** Solo dos locales, con temperaturas diarias correlacionadas a 0,96 entre sus
  estaciones. Hay muy poca variación climática independiente que explotar.
- **Asignación local–estación.** Es un supuesto, no un dato. Local y estación quedan perfectamente
  asociados, por lo que sus efectos no son separables (H5).
- **Variables omitidas.** No se dispone de precios, promociones, quiebres de stock ni publicidad, y del
  clima solo hay temperatura media diaria, sin lluvia ni humedad.
- **Pérdida de datos en el panel de la Fase 3.** La exigencia de ventanas completas al calcular las medias
  móviles anula los días posteriores a cualquier interrupción de una serie. El panel quedó con 29 fechas
  faltantes, todas de abril de 2021, y con 49 fechas que contienen un solo local en lugar de dos, de las
  cuales 20 caen dentro del conjunto de prueba. Esto reduce el entrenamiento disponible en torno a un
  16 % y hace que el Local X se evalúe sobre 23 de los 43 días de test, lo que explica buena parte de la
  diferencia entre su MAE (403,9) y el del Local Y (151,7). La corrección consiste en tolerar ventanas
  parciales (4 días válidos de 7 y 14 de 28); quedó identificada y no se alcanzó a reprocesar dentro del
  plazo de entrega. **No afecta a las conclusiones de la Fase 2**, obtenidas sobre la serie diaria de 271
  días y no sobre este panel.
- **Causalidad.** Todos los resultados son asociaciones estadísticas sobre datos observacionales y no
  habilitan afirmaciones causales. La importancia por permutación mide aporte predictivo, no causa.

---

## 10. Licencia y uso
Trabajo académico. Los datos de ventas fueron provistos por la cátedra y se utilizan exclusivamente con
fines educativos.
