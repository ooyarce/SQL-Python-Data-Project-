import pandas as pd

# Crear un DataFrame de ejemplo con 5 filas y 10 columnas
datos = pd.DataFrame({'col1': [1, 2, 3, 4, 5],
                      'col2': [6, 7, 8, 9, 10],
                      'col3': [11, 12, 13, 14, 15],
                      'col4': [16, 17, 18, 19, 20],
                      'col5': [21, 22, 23, 24, 25],
                      'col6': [26, 27, 28, 29, 30],
                      'col7': [31, 32, 33, 34, 35],
                      'col8': [36, 37, 38, 39, 40],
                      'col9': [41, 42, 43, 44, 45],
                      'col10': [46, 47, 48, 49, 50]})

# Seleccionar las cuatro columnas de interés por su nombre
cols_interes = ['col3', 'col4', 'col7', 'col9']
datos_interes = datos[cols_interes]

# Calcular el promedio de los valores de las cuatro columnas para cada fila
promedio_filas = datos_interes.mean(axis=1)

print(promedio_filas)
