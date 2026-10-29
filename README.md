# Grupo 10 — Proyecto Integrador de Ciencia de Datos

Impacto de las condiciones meteorológicas sobre las ventas diarias de un comercio minorista.

Universidad Nacional de Asunción — Facultad Politécnica · Ingeniería Informática · Data Science (electiva)

---

## Pregunta de investigación

> ¿En qué medida las condiciones meteorológicas diarias explican la variación en la cantidad de unidades
> vendidas por local, y en qué secciones o categorías de productos se evidencian los mayores efectos de
> ventas cruzadas o sustitución al aislar los factores de calendario?

**Objetivo general:** analizar el efecto de las variables meteorológicas sobre el volumen de unidades
vendidas a nivel de local y jerarquía de producto, aislando los factores de calendario mediante modelos
de ciencia de datos.

El proyecto sigue la metodología **CRISP-DM**, desarrollada en tres fases acumulativas sobre el mismo
conjunto de datos.

---

## Integrantes

| Nombre | Usuario de GitHub | Responsabilidad principal |
|---|---|---|
| Leyda Fleitas | `leydafleitas` | Fase 1 (preparación de datos) · Fase 3 Parte 1 (diseño del experimento) |
| _(completar)_ | _(completar)_ | _(completar)_ |
| _(completar)_ | _(completar)_ | _(completar)_ |

---

## Datos

### Fuentes

| Fuente | Contenido | Cobertura real |
|---|---|---|
| `ventas.csv` | 9.447.662 registros transaccionales a nivel ítem/sucursal | 271 días — **enero a septiembre de 2021** |
| `metereologia.csv` | Temperatura diaria por estación meteorológica | 660 registros = 20 estaciones × 33 meses (enero 2019 a septiembre 2021) |

### Nota sobre la cobertura temporal

El perfilado inicial de la Fase 1 declaraba "3 años continuos (2019–2021)" y "36 meses" de datos
meteorológicos. Al construir la serie agregada diaria en la Fase 2 se detectó que la cobertura real es
menor y se verificó el origen de la diferencia:

- El archivo meteorológico cubre **33 meses**, no 36.
- El archivo de ventas cubre **271 días de 2021**, sin transacciones de 2019 ni de 2020.
- El cruce entre ambas fuentes no produjo pérdida de registros (9.447.662 antes y después del `merge`,
  con 0 filas sin temperatura asignada): la diferencia proviene de la cobertura del archivo de ventas,
  no del proceso de preparación.

La documentación de la Fase 1 fue corregida en consecuencia. Toda conclusión del proyecto vale para el
período enero–septiembre de 2021 y no para un ciclo estacional completo.

### Unidades de análisis

| Fase | Unidad | Observaciones |
|---|---|---|
| Fase 1 | Transacción (ítem × sucursal × fecha) | 9.447.662 |
| Fase 2 | Según la hipótesis: serie diaria, panel fecha × local × sección, o transacción | 271 a 4.860 |
| Fase 3 | Panel fecha × local × sección | 3.429 filas utilizables (9 secciones × 2 locales) |

---

## Estructura del repositorio

```
.
├── data/          Conjuntos de datos derivados y livianos (panel de modelado)
├── docs/          Informes y documentación de las fases
├── notebooks/     Notebooks ejecutados de cada fase
├── output/        Artefactos generados: configuraciones, métricas, modelos
├── src/           Código reutilizable (funciones compartidas entre fases)
├── requirements.txt
└── README.md
```

> **Pendiente de orden:** la carpeta `fase2/` en la raíz quedó de una organización anterior. Antes de la
> entrega final conviene consolidar su contenido en `notebooks/`, `docs/` y `output/` según corresponda,
> ya que la consigna evalúa el repositorio final ordenado.

### Archivos que no están versionados

Por su tamaño, los datos originales y el dataset integrado no se incluyen en el repositorio:

| Archivo | Tamaño | Cómo obtenerlo |
|---|---|---|
| `ventas.csv` | ~917 MB | Fuente provista por la cátedra |
| `df_final.parquet` | ~70 MB | Se regenera ejecutando el notebook de la Fase 1 |

Ambos están excluidos mediante `.gitignore`. El panel de modelado derivado
(`data/panel_modelado.parquet`, ~150 KB) sí está versionado, porque es liviano y es la entrada directa de
la Fase 3.

---

## Requisitos

- Python 3.10 o superior
- Las dependencias listadas en `requirements.txt`

```bash
pip install -r requirements.txt
```

Los notebooks están preparados para ejecutarse en **Google Colab**, montando la carpeta compartida del
proyecto en Drive. Cada notebook define al inicio una variable de ruta que debe ajustarse según dónde esté
montada la carpeta:

```python
RUTA_BASE = "/content/drive/MyDrive/grupo10_data_science"
```

---

## Cómo reproducir el trabajo

Los notebooks deben ejecutarse **en orden**, porque cada uno consume artefactos generados por el anterior.

### 1. Fase 1 — Preparación de datos y análisis exploratorio

```
notebooks/fase1.ipynb
notebooks/fase1_dataset_final.ipynb
```

Limpia los datos meteorológicos (asteriscos a nulos, reestructuración de formato ancho a largo,
imputación por interpolación lineal), convierte tipos, asigna una estación meteorológica a cada local,
cruza ambas fuentes y agrega las variables de calendario.

**Produce:** `df_final.parquet` — dataset integrado de 9.447.662 registros con clima y calendario.

### 2. Fase 2 — Inferencia estadística

```
notebooks/fase2-Completo.ipynb
```

Contrasta las cinco hipótesis derivadas del análisis exploratorio, con verificación de supuestos,
tamaños de efecto y corrección por comparaciones múltiples.

**Consume:** `df_final.parquet` · **Produce:** tabla resumen de contrastes y el informe de la fase.

### 3. Fase 3 — Análisis predictivo

```
notebooks/fase3_parte1_diseno_experimento.ipynb     (Parte 1 — completada)
notebooks/fase3_parte2_modelado.ipynb               (Parte 2 — pendiente)
notebooks/fase3_parte3_evaluacion.ipynb             (Parte 3 — pendiente)
```

**Parte 1** define la tarea predictiva, construye el panel de modelado, realiza la partición cronológica
y establece las líneas base.

**Consume:** `df_final.parquet`
**Produce:** `data/panel_modelado.parquet`, `output/config_fase3.json`, `src/metricas_fase3.py`

**Parte 2** entrena los modelos sobre `particion == 'train'`, con validación cruzada temporal.
**Parte 3** evalúa sobre `particion == 'test'` una sola vez, analiza errores, interpreta el modelo y lo
serializa.

### Reproducibilidad

- Semilla fija: `SEMILLA = 42` en todas las fases.
- Toda transformación se realiza por código desde los archivos originales; no se edita ningún dato a mano.
- Los notebooks se ejecutan de principio a fin en un entorno limpio y regeneran sus salidas.

---

## Resultados por fase

### Fase 1 — Preparación y exploración

Dataset integrado de 9.447.662 registros, sin pérdida ni duplicación en el cruce. El análisis exploratorio
identificó estacionalidad semanal marcada, alta heterogeneidad en el tamaño de las transacciones y
diferencias de sensibilidad climática entre secciones comerciales, que dieron lugar a cinco hipótesis.

### Fase 2 — Inferencia estadística

| Hipótesis | Prueba | Resultado |
|---|---|---|
| **H1** — Las ventas de la sección más sensible (Bebidas) difieren por grupo climático | ANOVA de 2 factores + Tukey HSD | Se rechaza H0 (p = 2,7e-13), pero con tamaño de efecto insignificante (η² = 0,0001). Con errores agrupados por fecha, p = 0,18 |
| **H2** — La temperatura se asocia a las ventas totales diarias | Regresión lineal múltiple (OLS) | **No se rechaza H0** (p = 0,254). Domina el calendario: fin de semana y feriados son significativos |
| **H3** — El efecto del clima difiere entre secciones | Wald F robusto + corrección de Holm | Se rechaza H0 (p = 3,2e-49), magnitud modesta (−2,2 % a +1,3 % por °C). Solo Tienda, Almacén y Producción resisten la corrección |
| **H4** — El fin de semana modera el efecto climático | OLS con interacción, errores HC3 | **No se rechaza H0** (p = 0,91) |
| **H5** — El efecto climático varía por local | Wald F robusto + bootstrap por clusters | **No se rechaza H0** (p = 0,092). Local y estación están perfectamente asociados: no son separables |

**Lectura conjunta:** la evidencia no respalda que el clima explique una porción relevante de la variación
de ventas. Los efectos detectados son pequeños y dependen de cómo se trate la estacionalidad. El calendario
es, con diferencia, el factor dominante.

### Fase 3 — Análisis predictivo

**Tarea:** regresión. **Objetivo:** unidades vendidas por día, local y sección. **Horizonte:** t+1.

Partición cronológica con corte el **19 de agosto de 2021**: 2.835 filas de entrenamiento y 594 de prueba.

| Línea base | RMSE | MAE | MAPE | R² |
|---|---|---|---|---|
| Media por local × sección | 1077,2 | 603,8 | 67,4 % | 0,781 |
| **Ingenua estacional (lag-7)** | **700,6** | **318,0** | **39,5 %** | **0,907** |

La línea base a superar es la **ingenua estacional**, no la de la media. En series con estacionalidad
semanal fuerte, predecir el valor del mismo día de la semana anterior ya alcanza un R² de 0,907: un modelo
que no supere ese valor no justifica su existencia.

_(Resultados del modelado y la evaluación: pendientes de las Partes 2 y 3.)_

---

## Decisiones metodológicas relevantes

| Decisión | Fundamento |
|---|---|
| Asignación manual de local a estación meteorológica | El dataset no incluye información geográfica real de los locales ('Local X', 'Local Y'). Supuesto simplificador documentado explícitamente |
| Nulos estructurales eliminados, no imputados | Corresponden a fechas inexistentes (ej. 30 de febrero) generadas por la matriz de 31 columnas del archivo original |
| Panel reindexado sobre el calendario completo (Fase 3) | Garantiza que `lag_7` signifique siete días y no siete filas: un día faltante correría todos los rezagos posteriores |
| Celdas sin ventas conservadas como nulas, no como cero | Un día sin registros es un día sin operación del local, no un día de cero ventas |
| Partición cronológica, nunca aleatoria | Los datos tienen componente temporal: entrenar con el futuro para predecir el pasado invalida la evaluación |
| Temperatura del día `t` como predictora | Supone disponer del pronóstico, que es el escenario de uso planteado. Supuesto optimista: el pronóstico real tiene error propio |
| Tamaños de efecto reportados junto a los p-valores | Con cientos de miles de observaciones, diferencias triviales resultan estadísticamente significativas |

---

## Limitaciones

- **Cobertura temporal:** enero a septiembre de 2021, un único año parcial. No incluye el verano completo
  ni un ciclo estacional cerrado, lo que acota el rango de temperaturas observado.
- **Resolución espacial:** solo dos locales, con temperaturas diarias correlacionadas a 0,96 entre sus
  estaciones. Hay muy poca variación climática independiente.
- **Asignación local–estación:** es un supuesto, no un dato. Local y estación quedan perfectamente
  asociados, por lo que sus efectos no son separables.
- **Causalidad:** todos los resultados son asociaciones estadísticas sobre datos observacionales. No
  habilitan afirmaciones causales.

---

## Licencia y uso

Trabajo académico. Los datos de ventas fueron provistos por la cátedra y se utilizan exclusivamente con
fines educativos.
