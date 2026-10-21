"""Transformaciones compartidas entre el notebook y la aplicación Flask.

El Pipeline guardado en modelos/ recibe SOLO los predictores crudos (BASE, en este orden)
y calcula adentro las variables derivadas. Así la aplicación no puede calcularlas distinto
que en el entrenamiento. Solo usa numpy para que el despliegue sea liviano.
"""
import numpy as np

# Orden obligatorio de las columnas de entrada (10 predictores crudos).
BASE = ['Temp', 'Hum', 'Pres', 'GHI', 'viento_vel', 'Holiday',
        'hora', 'dia_semana', 'mes', 'fin_de_semana']

# Temperatura de menor demanda en el entrenamiento 2012-2016 (calculada en el notebook).
T_CONFORT = 18.0

NOMBRES_DERIVADAS = ['temp_confort', 'hora_sin', 'hora_cos', 'mes_sin', 'mes_cos']

_I_TEMP = BASE.index('Temp')
_I_HORA = BASE.index('hora')
_I_MES = BASE.index('mes')


def agregar_derivadas(X):
    """Recibe un arreglo (n, 10) con las columnas de BASE y devuelve (n, 15)."""
    X = np.asarray(X, dtype=float)
    temp_confort = np.abs(X[:, _I_TEMP] - T_CONFORT)
    hora = X[:, _I_HORA]
    mes = X[:, _I_MES]
    derivadas = np.column_stack([
        temp_confort,
        np.sin(2 * np.pi * hora / 24),
        np.cos(2 * np.pi * hora / 24),
        np.sin(2 * np.pi * (mes - 1) / 12),
        np.cos(2 * np.pi * (mes - 1) / 12),
    ])
    return np.hstack([X, derivadas])
