# Datos

## Fuente
El conjunto se obtuvo del portal **Datos Argentina**, en el catálogo de la Secretaría de Energía, y contiene demanda eléctrica horaria del Gran Buenos Aires atribuida a CAMMESA. [Consultar el catálogo](https://datos.gob.ar/dataset/?organization=secretaria-de-energia).

Para una cita plenamente reproducible todavía falta identificar la ficha exacta del recurso descargado, documentar el origen de las variables climáticas y del EMAE, y describir la limpieza previa que llevó al archivo `cammesa_limpio.csv`.

## Archivos
| Archivo | Descripción |
|---|---|
| `cammesa_limpio.csv` | Dato de partida: 61.368 horas (01/01/2012 a 31/12/2018), 18 columnas. |
| `cammesa_preparado.csv` | Dataset preparado por el notebook: 61.368 filas y 23 columnas, sin faltantes en los predictores. |
| `resultados_entrega2.json` | Controles de calidad, balance de clases y resultados de los baselines (los usa el informe). |
| `resultados_entrega3_4.json` | Resultados de regresión, clasificación, comparación de los dos sistemas y sensibilidad de costos (los usa el informe). |

Cada fila es una hora del GBA. Para obtener `cammesa_preparado.csv` se ejecuta `notebooks/entrenamiento.ipynb`.

## Objetivos
- **Regresión:** `DemGBA`, demanda horaria en MW.
- **Clasificación:** `alta_demanda = 1` si `DemGBA > 7.307` MW (percentil 90 del entrenamiento); 0 en caso contrario.

## Preparación aplicada
- Faltantes de `Temp`, `Hum`, `Pres`, `vx`, `vy` (tramos de hasta 5 horas): interpolación lineal en el tiempo; `viento_vel` se recalcula.
- Faltantes de `GHI` (días completos): media por mes y hora calculada solo con entrenamiento.
- Variables derivadas: `temp_confort`, `hora_sin`, `hora_cos`, `mes_sin`, `mes_cos`.
- Partición temporal en la columna `split`: `train` (2012–2016), `valid` (2017) y `test` (2018).

## Diccionario de variables
| Variable | Descripción | Unidad / rango | Rol |
|---|---|---|---|
| `datetime` | Fecha y hora de la observación (paso horario). | 2012-01-01 a 2018-12-31 | Identificador |
| `split` | Partición temporal. | train / valid / test | Control |
| `DemGBA` | Demanda eléctrica horaria del GBA. | MW; 2.803 a 9.929 | Objetivo (regresión) |
| `alta_demanda` | 1 si `DemGBA` > 7.307 MW. | 0 / 1 | Objetivo (clasificación) |
| `Temp` | Temperatura del aire. | °C; 0,4 a 37,9 | Predictor |
| `Hum` | Humedad relativa. | Fracción; 0,15 a 1,00 | Predictor |
| `Pres` | Presión atmosférica. | hPa; 993,8 a 1.037,9 | Predictor |
| `GHI` | Radiación solar global horizontal. | Unidad a confirmar; 0 a 1.136 | Predictor |
| `viento_vel` | Intensidad del viento, raíz de vx² + vy². | Unidad a confirmar; 0,0 a 39,5 | Predictor |
| `vx`, `vy` | Componentes del viento. | Unidad a confirmar | Opcional |
| `Holiday` | Feriado. | 0 / 1 | Predictor |
| `EMAE` | Estimador mensual de actividad económica (un valor por mes). | Índice; 143,5 a 151,4 | Descartado como predictor |
| `hora` | Hora del día. | 0 a 23 | Predictor |
| `dia_semana` | Día de la semana. | 0 (lunes) a 6 (domingo) | Predictor |
| `mes` | Mes del año. | 1 a 12 | Predictor |
| `fin_de_semana` | Sábado o domingo. | 0 / 1 | Predictor |
| `temp_confort` | Distancia absoluta de `Temp` a 18 °C (temperatura de menor demanda en entrenamiento). | °C; 0,0 a 19,9 | Derivada |
| `hora_sin`, `hora_cos` | Hora en seno y coseno. | -1 a 1 | Derivada |
| `mes_sin`, `mes_cos` | Mes en seno y coseno. | -1 a 1 | Derivada |
| `falla_sensor` | Marca las 12 horas sin datos de clima por falla del sensor. | 0 / 1 | Control (no es predictor) |

## Predictores que usan los modelos
Los Pipelines guardados en `modelos/` reciben **10 columnas crudas**, en este orden: `Temp`, `Hum`, `Pres`, `GHI`, `viento_vel`, `Holiday`, `hora`, `dia_semana`, `mes`, `fin_de_semana`. Dentro del Pipeline (`features.py`) se calculan 5 derivadas: `temp_confort`, `hora_sin`, `hora_cos`, `mes_sin`, `mes_cos`.

**Momento de la predicción:** se estima la demanda de una hora futura con el calendario de esa hora y el pronóstico meteorológico para esa hora. En el entrenamiento se usa clima medido, no pronosticado.

## Variables descartadas como predictores
| Variable | Motivo |
|---|---|
| `DemGBA`, `alta_demanda` | Son los objetivos. |
| `datetime`, `split` | Identificador temporal y marca de partición. |
| `falla_sensor` | Indicador de calidad del dato; no se conoce al predecir. |
| `vx`, `vy` | Redundantes con `viento_vel`. |
| `EMAE` | Se publica con retraso (no estaría disponible al predecir) y empeora el error de validación: con el árbol, de 351 a 449 MW (variables base) y de 330 a 387 MW (con derivadas). Es un valor único por mes y actúa como identificador de período. |
| Demanda de horas anteriores (rezagos) | La consigna prohíbe que la respuesta aparezca directa o indirectamente entre las entradas. |
