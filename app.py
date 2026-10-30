"""Aplicación Flask: demanda eléctrica del GBA (regresión + alerta de alta demanda).

Solo carga los Pipelines guardados en modelos/ con joblib y ejecuta predict.
No entrena en cada solicitud y no acepta archivos joblib/pickle externos.
Los modelos se entrenaron en notebooks/entrenamiento.ipynb.
"""
import json
import os
from datetime import datetime

import joblib
import numpy as np
from flask import Flask, jsonify, render_template, request

import features  # noqa: F401  (los Pipelines guardados referencian features.agregar_derivadas)
from features import BASE

AQUI = os.path.dirname(os.path.abspath(__file__))

# En Vercel los estáticos se sirven desde public/; en local los sirve Flask desde la misma carpeta.
app = Flask(__name__, static_folder=os.path.join(AQUI, 'public'), static_url_path='')

# ---- Carga única al iniciar (no se entrena ni se cargan archivos del usuario) ----
REGRESOR = joblib.load(os.path.join(AQUI, 'modelos', 'regresor.joblib'))
CLASIFICADOR = joblib.load(os.path.join(AQUI, 'modelos', 'clasificador.joblib'))
with open(os.path.join(AQUI, 'modelos', 'metadatos.json'), encoding='utf-8') as f:
    META = json.load(f)

UMBRAL = float(META['umbral_MW'])
MARGEN = float(META['margen_precaucion_MW'])
MAE = float(META['mae_test_MW'])

# ---- Rangos de validación de los campos del formulario ----
# Límites físicos amplios (no los del entrenamiento), para rechazar solo valores imposibles.
CAMPOS = [
    # nombre, etiqueta, mínimo, máximo, paso, ayuda
    ('temp', 'Temperatura pronosticada (°C)', -10, 50, 0.1, 'En el entrenamiento: 0,4 a 37,9 °C'),
    ('hum', 'Humedad relativa (%)', 0, 100, 1, 'En el entrenamiento: 15 a 100 %'),
    ('pres', 'Presión atmosférica (hPa)', 900, 1100, 0.1, 'En el entrenamiento: 994 a 1.038 hPa'),
    ('ghi', 'Radiación solar global horizontal (GHI)', 0, 1400, 1, 'De noche es 0. En el entrenamiento: 0 a 1.136'),
    ('viento', 'Intensidad del viento', 0, 100, 0.1, 'Misma unidad que el dataset. En el entrenamiento: 0 a 39,5'),
]
FECHA_MIN, FECHA_MAX = '2019-01-01', '2035-12-31'
EJEMPLO = {'fecha': '2026-01-15', 'hora': '17', 'temp': '33', 'hum': '45', 'pres': '1008',
           'ghi': '700', 'viento': '10', 'feriado': ''}


def _numero(valores, nombre, etiqueta, minimo, maximo, errores):
    """Convierte un campo a número y lo valida. Agrega un mensaje a errores si falla."""
    texto = (valores.get(nombre) or '').strip().replace(',', '.')
    if texto == '':
        errores[nombre] = f'Completá: {etiqueta}.'
        return None
    try:
        x = float(texto)
    except ValueError:
        errores[nombre] = f'{etiqueta}: ingresá un número.'
        return None
    if not np.isfinite(x) or x < minimo or x > maximo:
        errores[nombre] = f'{etiqueta}: el valor debe estar entre {minimo} y {maximo}.'
        return None
    return x


def validar(valores):
    """Devuelve (entrada, errores). entrada es un dict con las columnas de BASE si no hay errores."""
    errores, nums = {}, {}
    for nombre, etiqueta, mn, mx, _paso, _ayuda in CAMPOS:
        nums[nombre] = _numero(valores, nombre, etiqueta, mn, mx, errores)

    fecha = None
    try:
        fecha = datetime.strptime((valores.get('fecha') or '').strip(), '%Y-%m-%d')
        if not (FECHA_MIN <= fecha.strftime('%Y-%m-%d') <= FECHA_MAX):
            errores['fecha'] = f'La fecha debe estar entre {FECHA_MIN} y {FECHA_MAX}.'
    except ValueError:
        errores['fecha'] = 'Ingresá una fecha válida.'

    hora = _numero(valores, 'hora', 'Hora del día', 0, 23, errores)
    if hora is not None and hora != int(hora):
        errores['hora'] = 'Hora del día: ingresá un número entero entre 0 y 23.'

    if errores:
        return None, errores

    entrada = {
        'Temp': nums['temp'], 'Hum': nums['hum'] / 100.0, 'Pres': nums['pres'], 'GHI': nums['ghi'],
        'viento_vel': nums['viento'], 'Holiday': 1.0 if valores.get('feriado') else 0.0,
        'hora': float(int(hora)), 'dia_semana': float(fecha.weekday()), 'mes': float(fecha.month),
        'fin_de_semana': 1.0 if fecha.weekday() >= 5 else 0.0,
    }
    return entrada, {}


def predecir(entrada):
    """Ejecuta los dos Pipelines guardados sobre un caso."""
    x = np.array([[entrada[c] for c in BASE]], dtype=float)
    mw = float(REGRESOR.predict(x)[0])
    alerta_reg = mw > UMBRAL
    alerta_clf = bool(CLASIFICADOR.predict(x)[0])
    proba = float(CLASIFICADOR.predict_proba(x)[0, 1]) if hasattr(CLASIFICADOR, 'predict_proba') else None
    alerta_prev = mw > UMBRAL - MARGEN
    dif = mw - UMBRAL
    cercano = abs(dif) <= MAE

    # Avisos si algún dato queda fuera de lo que el modelo vio en el entrenamiento (2012-2016).
    avisos = []
    etiquetas = {'Temp': 'La temperatura', 'Hum': 'La humedad', 'Pres': 'La presión',
                 'GHI': 'La radiación solar', 'viento_vel': 'El viento'}
    for col, nombre in etiquetas.items():
        mn, mx = META['rangos_entrenamiento'][col]
        if not (mn <= entrada[col] <= mx):
            avisos.append(f'{nombre} ingresada está fuera del rango que vio el modelo al entrenar: '
                          'la predicción es una extrapolación y es menos confiable.')

    if alerta_reg and alerta_clf:
        coincidencia, nivel = 'Los dos sistemas coinciden: alta demanda.', 'alta'
        texto = ('Ambos sistemas anticipan que la demanda superaría el umbral. '
                 'Conviene preparar generación y reserva adicional para esa hora.')
    elif (not alerta_reg) and (not alerta_clf):
        coincidencia, nivel = 'Los dos sistemas coinciden: sin alerta.', 'normal'
        texto = ('Ninguno de los dos sistemas anticipa alta demanda para esa hora. '
                 'No se requiere reserva adicional según este modelo.')
    else:
        coincidencia, nivel = 'Desacuerdo entre los dos sistemas.', 'desacuerdo'
        texto = ('Un sistema alerta y el otro no. Es una señal de que el caso está cerca del umbral y '
                 'conviene revisarlo con criterio operativo antes de decidir. Con el esquema de costos '
                 'del proyecto (un pico no anticipado cuesta más que una reserva de más), se recomienda '
                 'priorizar la alerta del clasificador directo.')
    return {
        'mw': mw, 'umbral': UMBRAL, 'dif': dif, 'alerta_reg': alerta_reg, 'alerta_clf': alerta_clf,
        'proba': proba, 'alerta_prev': alerta_prev, 'margen': MARGEN, 'cercano': cercano, 'mae': MAE,
        'coincidencia': coincidencia, 'nivel': nivel, 'texto': texto, 'avisos': avisos,
    }


@app.template_filter('miles')
def miles(valor, decimales=0):
    """Formato argentino: 7.307 o 7.307,5."""
    s = f'{valor:,.{decimales}f}'
    return s.replace(',', '#').replace('.', ',').replace('#', '.')


@app.route('/', methods=['GET'])
def inicio():
    return render_template('index.html', campos=CAMPOS, valores=EJEMPLO, errores={}, resultado=None,
                           meta=META, fecha_min=FECHA_MIN, fecha_max=FECHA_MAX)


@app.route('/predecir', methods=['POST'])
def predecir_ruta():
    valores = request.form.to_dict()
    entrada, errores = validar(valores)
    resultado = predecir(entrada) if not errores else None
    return render_template('index.html', campos=CAMPOS, valores=valores, errores=errores, resultado=resultado,
                           meta=META, fecha_min=FECHA_MIN, fecha_max=FECHA_MAX), (400 if errores else 200)


@app.route('/api/predecir', methods=['POST'])
def api_predecir():
    datos = request.get_json(silent=True) or {}
    valores = {k: ('' if v is None else str(v)) for k, v in datos.items() if k != 'feriado'}
    valores['feriado'] = '1' if datos.get('feriado') is True else ''
    entrada, errores = validar(valores)
    if errores:
        return jsonify(errores=errores), 400
    return jsonify(predecir(entrada))


@app.route('/salud')
def salud():
    return {'estado': 'ok', 'regresor': META['regresor'], 'clasificador': META['clasificador']}


if __name__ == '__main__':
    app.run(debug=False, port=int(os.environ.get('PORT', 5000)))
