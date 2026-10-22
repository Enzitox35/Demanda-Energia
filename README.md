# Demanda eléctrica del GBA: regresión y alerta de alta demanda

TP Integrador de Aprendizaje Automático · Instituto de Formación Docente y Técnica N.º 57 · Chascomús

**Integrantes:** Enzo Mellado, Gladys González y Lucas Pardo  
**Curso:** 2.º año de Ciencia de Datos e Inteligencia Artificial

El equipo continúa con tres integrantes, con autorización del docente luego de la baja de un integrante.

## Qué hace el proyecto
Sobre datos horarios de demanda eléctrica del Gran Buenos Aires (CAMMESA, 2012–2018) se resuelven dos tareas relacionadas:

- **Regresión:** estimar la demanda horaria `DemGBA` en MW.
- **Clasificación:** anticipar si la demanda supera el umbral de alta demanda (7.307 MW, el percentil 90 del entrenamiento).

La alerta se genera de dos maneras, un clasificador directo y la regresión más el umbral, y se comparan. Decisión que apoya: activar o no generación y reserva adicional para la hora a cubrir.

## Resultados principales (prueba 2018)
| Sistema | Accuracy | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|---|
| Clasificador directo (árbol, prof. 8, pesos 1:5) | 0,922 | 0,672 | 0,867 | 0,757 | 517 | 162 |
| Regresión + umbral (árbol de regresión, prof. 12) | 0,929 | 0,812 | 0,635 | 0,713 | 180 | 446 |

- **Regresión:** MAE de 413 MW en prueba, contra 1.019 MW del `DummyRegressor` y 611 MW de la referencia estacional.
- **Recomendación:** con un falso negativo 5 veces más costoso que un falso positivo, el clasificador directo es la alerta principal (costo 45 % menor); la regresión informa los MW esperados y sirve de control cruzado.
- El detalle, las limitaciones y las respuestas a las preguntas del informe están en el notebook (secciones 10 a 13).

## Informe final
- [Leer el informe web con gráficos y resultados](informe/informe_web.html).
- [Abrir el informe final en Word](informe/entregas/Informe_final_Demanda_electrica_GBA.docx).
- [Ver la presentación](informe/entregas/Demanda_electrica_GBA.pptx).

## Estructura del repositorio
```
├── README.md
├── requirements.txt             dependencias de la aplicación (las instala Vercel)
├── requirements-notebook.txt    dependencias para ejecutar el notebook
├── app.py                       aplicación Flask
├── features.py                  variables derivadas (las usan el notebook y la app)
├── vercel.json, .vercelignore   configuración del despliegue
├── modelos/                     Pipelines guardados con joblib + metadatos.json
├── templates/                   plantilla HTML de la aplicación
├── public/                      archivos estáticos (estilos.css)
├── notebooks/entrenamiento.ipynb
├── datos/
│   ├── README.md                fuente, diccionario y preparación
│   ├── cammesa_limpio.csv       dato de partida
│   ├── cammesa_preparado.csv    dataset preparado (Entrega 2)
│   ├── resultados_entrega2.json
│   └── resultados_entrega3_4.json
└── informe/
    ├── informe_web.html         versión web del informe, con gráficos y logos
    ├── entregas/                documentos de cada entrega
    ├── figuras/
    │   ├── logo-instituto-57.png
    │   └── logo-cammesa.png
    ├── entregas/bitacora.md     decisiones tomadas
    └── entregas/distribucion_tareas.md
```

## Cómo ejecutar el notebook
```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements-notebook.txt
jupyter lab notebooks/entrenamiento.ipynb
```
El notebook se ejecuta de principio a fin desde la carpeta `notebooks/` (rutas relativas a `../datos`) y regenera el dataset preparado, las figuras, los resultados en JSON y los modelos de `modelos/`. Se ejecutó con Python 3.12 y las versiones de `requirements.txt` y `requirements-notebook.txt`. Semilla: 42.

> Si se vuelve a ejecutar el notebook con otras versiones de scikit-learn o numpy, los Pipelines nuevos solo se podrán cargar con esas mismas versiones.

## Cómo ejecutar la aplicación
```bash
pip install -r requirements.txt
python app.py                    # abre http://127.0.0.1:5000
```
La aplicación solo carga los Pipelines de `modelos/` y ejecuta `predict`. No entrena, no usa base de datos ni acepta archivos joblib o pickle del usuario.

## Despliegue en Vercel
1. Subir el repositorio a GitHub (con la carpeta `modelos/` incluida).
2. En Vercel: **Add New → Project**, importar el repositorio y dejar la configuración por defecto. Vercel detecta Flask por `app.py` y toma las dependencias de `requirements.txt`; los archivos de `public/` se sirven como estáticos.
3. Revisar el *build log* y abrir la URL `proyecto.vercel.app`.
4. Probar desde otro dispositivo y completar la URL de abajo.

## Estado de las entregas
| Entrega | Contenido | Etiqueta | Estado |
|---|---|---|---|
| 1 | Propuesta con tres alternativas | `entrega-1-propuesta` | Hecha |
| 2 | Datos preparados, diccionario, objetivos, protocolo y baselines | `entrega-2-datos` | Hecha |
| 3 | Regresores (Dummy, árbol, KNN) | `entrega-3-regresion` | Código y análisis listos; falta crear la etiqueta |
| 4 | Clasificadores, comparación de los dos sistemas, modelos guardados y app local | `entrega-4-clasificacion` | Código y análisis listos; falta crear la etiqueta |
| 5 | Publicación en Vercel, presentación y defensa | `entrega-5-final` | Pendiente: despliegue, prueba desde otro dispositivo y defensa |

## Datos
Ver `datos/README.md`. La partición es temporal: entrenamiento 2012–2016, validación 2017 y prueba 2018.

## URL de la aplicación
[completar en la Entrega 5: proyecto.vercel.app]
