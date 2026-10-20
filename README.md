# Demanda eléctrica del GBA: regresión y alerta de alta demanda

TP Integrador de Aprendizaje Automático · Instituto 57

**Integrantes:** Enzo Mellado, Gladys González y Lucas Pardo  
**Curso:** 2do Año - Ciencia de Datos e IA · **Grupo:** 2.

## Qué hace el proyecto
Sobre datos horarios de demanda eléctrica del Gran Buenos Aires (CAMMESA, 2012–2018) se resuelven dos tareas relacionadas:

- **Regresión:** estimar la demanda horaria `DemGBA` en MW.
- **Clasificación:** anticipar si la demanda supera el umbral de alta demanda (7.307 MW, el percentil 90 del entrenamiento).

La alerta se genera de dos maneras, un clasificador directo y la regresión más el umbral, y se comparan. Decisión que apoya: activar o no generación y reserva adicional para la hora siguiente.

## Estructura del repositorio
```
├── README.md
├── requirements.txt
├── app.py                       aplicación Flask (Entrega 4 en adelante)
├── modelos/                     Pipelines guardados con joblib (Entrega 4)
├── templates/                   plantillas HTML de la aplicación
├── public/                      archivos estáticos
├── notebooks/entrenamiento.ipynb
├── datos/
│   ├── README.md                fuente, diccionario y preparación
│   ├── cammesa_limpio.csv       dato de partida
│   ├── cammesa_preparado.csv    dataset preparado (Entrega 2)
│   └── resultados_entrega2.json resultados que usa el informe
└── informe/
    ├── entregas/                documentos de cada entrega
    ├── figuras/
    ├── bitacora.md              decisiones tomadas
    ├── distribucion_tareas.md
    └── informe_final.pdf        (Entrega 5)
```

## Cómo ejecutarlo
```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install jupyterlab
jupyter lab notebooks/entrenamiento.ipynb
```
El notebook se ejecuta desde la carpeta `notebooks/` (rutas relativas a `../datos`). Se corrió con Python 3.12.

## Estado de las entregas
| Entrega | Contenido | Etiqueta | Estado |
|---|---|---|---|
| 1 | Propuesta con tres alternativas | `entrega-1-propuesta` | Hecha |
| 2 | Datos preparados, diccionario, objetivos, protocolo y baselines | `entrega-2-datos` | Hecha |
| 3 | Regresores (Dummy, árbol, KNN) | `entrega-3-regresion` | Pendiente |
| 4 | Clasificadores, comparación de los dos sistemas, modelos guardados y app local | `entrega-4-clasificacion` | Pendiente |
| 5 | Publicación en Vercel, presentación y defensa | `entrega-5-final` | Pendiente |

## Datos
Ver `datos/README.md`. La partición es temporal: entrenamiento 2012–2016, validación 2017 y prueba 2018.

## URL de la aplicación
[completar en la Entrega 5: proyecto.vercel.app]
