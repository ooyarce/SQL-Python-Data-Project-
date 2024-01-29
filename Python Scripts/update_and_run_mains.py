import os
import shutil
import subprocess
import sys

# Definir la ruta al nuevo archivo main_sql.py
nuevo_main_sql_path = "C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/Python Scripts/main_sql.py"

# Definir el directorio raíz que contiene las subcarpetas
directorio_raiz = "m6.5"

# Iterar a través de cada subcarpeta
for subdir in os.listdir(directorio_raiz):
    for subsubdir in os.listdir(os.path.join(directorio_raiz, subdir)):
        if subsubdir.startswith("station_s"):
            # Construye la ruta al archivo main_sql.py existente
            path_existente = os.path.join(directorio_raiz, subdir, subsubdir, "main_sql.py")

            # Copiar el nuevo main_sql.py a la subcarpeta
            shutil.copy(nuevo_main_sql_path, path_existente)

            # Informar que el archivo ha sido actualizado
            print('====================================================')
            print(f"File main_sql.py updated {path_existente}")

            # Ejecutar el script actualizado
            print(f"Running {path_existente}...")
            print('====================================================')
            result = subprocess.run(["python", path_existente], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            print('\n')