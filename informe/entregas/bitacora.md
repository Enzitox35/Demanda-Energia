# Bitácora de decisiones

| Entrega | Decisión | Motivo | Alternativas descartadas | Responsable |
|---|---|---|---|---|
| 1 | Trabajar con la demanda eléctrica del GBA (CAMMESA) | Cumple tamaño (61.368 filas), más de 10 predictores y un umbral con decisión operativa clara | Precio de nafta en surtidores: pocos predictores, precios de distintas fechas y tema ya visto en otra materia. Alquileres temporarios: fuente y tamaño por confirmar | [completar] |
| 1 | No usar el Excel anual de CAMMESA 2005–2025 | Solo 21 observaciones por variable, lejos de las 2.000 que pide la consigna | — | [completar] |
| 2 | Umbral de alta demanda = percentil 90 del entrenamiento (7.307 MW) | Criterio estadístico calculado sin mirar validación ni prueba | Percentil calculado sobre todo el período | [completar] |
| 2 | Partición temporal 2012–2016 / 2017 / 2018 | Es una serie temporal: se entrena con el pasado y se evalúa con el futuro | Partición aleatoria | [completar] |
| 2 | Interpolación lineal para faltantes cortos de clima y media mes-hora de entrenamiento para GHI | Los faltantes de GHI son días completos y la radiación tiene ciclo diario | Eliminar las filas; mediana global | [completar] |
| 2 | Agregar `temp_confort` y hora/mes en seno y coseno | La relación entre temperatura y demanda tiene forma de U, y hora y mes son circulares | Usar solo variables crudas | [completar] |
| 2 | No usar demanda de horas anteriores como predictor | La consigna prohíbe que la respuesta aparezca indirectamente entre las entradas | Rezagos de 24 y 168 horas (mejoraban el resultado); consultar al docente | [completar] |
| 2 | Costo del falso negativo = 5 veces el del falso positivo (provisorio) | Un pico no anticipado es más grave que una reserva activada sin necesidad | Relación 1 a 1; se hará análisis de sensibilidad | [completar] |
| 3 | Quitar `EMAE` de los predictores | No estaría disponible al predecir (se publica con retraso) y empeora la validación: árbol 351 → 449 MW con variables base y 330 → 387 MW con derivadas | Dejarla "con cautela" | [completar] |
| 3 | Calcular las variables derivadas dentro del Pipeline (`features.py`) | La app recibe solo datos crudos y calcula lo mismo que el entrenamiento; evita errores de coherencia | Calcularlas en `app.py` | [completar] |
| 3 | Elegir hiperparámetros solo con el MAE de validación: árbol de profundidad 12 y KNN con k = 15; regresor elegido: árbol | Regla definida de antemano; la prueba no se usa para decidir (en prueba empatan: 413 MW los dos) | Profundidad 10 (empate técnico en validación: 331 contra 330 MW); elegir con la prueba | [completar] |
| 3 | Mantener la regresión sin rezagos de demanda | La consigna lo prohíbe. **Pendiente: consultar al docente** si se permiten rezagos y registrar la respuesta | Rezagos de 24 y 168 horas | [completar] |
| 4 | Esquema de costos FN = 5 × FP, con análisis de sensibilidad de 1 a 20 | Un pico no anticipado es más grave que una reserva de más; el valor 5 es un supuesto y se prueba su efecto | Costos iguales (1 a 1) | [completar] |
| 4 | Elegir el clasificador por costo de validación; elegido: `DecisionTreeClassifier` de profundidad 8 con pesos de clase 1:5 | Con 10 % de positivos la accuracy no distingue entre modelos (KNN: 0,923 contra 0,922 del árbol, pero 525 contra 162 picos sin detectar en prueba) | Elegir por accuracy o por F1 | [completar] |
| 4 | Recomendar el clasificador directo como alerta principal y usar la regresión para informar los MW y como control cruzado | Con costos 1:5 el directo tiene un costo 45 % menor que la regresión + umbral fijo (1.327 contra 2.410 en prueba) | Usar solo regresión + umbral | [completar] |
| 4 | Incluir variantes ajustadas por costo (margen de 475 MW y corte de probabilidad 0,35) como análisis adicional | Muestran que parte de la desventaja de la regresión viene del umbral sin ajustar; se calibran solo con validación | No analizarlas | [completar] |
| 4 | Separar `requirements.txt` (aplicación) de `requirements-notebook.txt` (notebook) | Vercel instala `requirements.txt`; así se evita instalar pandas, matplotlib y Jupyter en el despliegue | Un único archivo | [completar] |
| 4 | Guardar los Pipelines entrenados solo con 2012–2016 (los mismos que se evalúan) | La aplicación usa los modelos presentados en el informe | Reentrenar con 2012–2017 para la app | [completar] |
