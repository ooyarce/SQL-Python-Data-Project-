from pathlib import Path
import subprocess
import shutil
import sys
import time

# Definir la ruta al nuevo archivo main_sql.py
nuevo_main_sql_path = Path("C:/Users/oioya/OneDrive - miuandes.cl/Escritorio/Git-Updated/Thesis-Project-Simulation-Data-Analysis/Python Scripts/main_sql.py")

# Definir los tipos de simulación, estructuras, magnitudes, tipos de ruptura y estaciones
tipos_simulacion = ['FixBase', 'AbsBound', 'DRM']
estructuras      = ['20f2s', '20f4s', '55f4s', '55f7s']
magnitudes       = ['m6.7', 'm6.9', 'm7.0']
tipos_ruptura    = ['rup_bl_1', 'rup_bl_2', 'rup_bl_3']
estaciones       = [f'station_s{i}' for i in range(10)]  # Genera 'station_s0' hasta 'station_s9'

# Archivos a eliminar
archivos_eliminar = ["analysis_steps.tcl","elements.tcl","main.tcl","materials.tcl","nodes.tcl","sections.tcl","*.mpco","*.mpco.cdata","import_h5py.py","input.h5drm"]
def eliminar_archivos(path):
    for archivo in archivos_eliminar:
        for file_path in path.glob(archivo):
            try:
                file_path.unlink()
                print(f"Archivo {file_path} eliminado.")
            except Exception as e:
                print(f"Archivos previamente eliminados en {file_path}: {e}")

# Directorio raíz donde se encuentran los tipos de simulación
directorio_raiz = Path(__file__).parent

# Iterar a través de cada tipo de simulación
# Calcular inicio de tiempo
start_time = time.time()
for tipo in tipos_simulacion:

    for estructura in estructuras:
        path_estructuras = directorio_raiz / tipo / estructura
        if not path_estructuras.exists():
            continue

        for magnitud in magnitudes:
            path_magnitud = path_estructuras / magnitud
            if not path_magnitud.exists():
                continue

            for tipo_ruptura in tipos_ruptura:
                path_tipo_ruptura = path_magnitud / tipo_ruptura
                if not path_tipo_ruptura.exists():
                    continue

                for estacion in estaciones:
                    path_estacion = path_tipo_ruptura / estacion
                    if not path_estacion.exists():
                        continue

                    # Copiar el nuevo main_sql.py a la subcarpeta si el archivo existe
                    path_existente = path_estacion / "main_sql.py"
                    shutil.copy(nuevo_main_sql_path, path_existente)

                    # Informar que el archivo ha sido actualizado
                    print('====================================================')
                    print(f"File main_sql.py updated in {path_existente}")

                    ## Intentar ejecutar el script actualizado y eliminar archivos si es exitoso
                    try:
                        print(f"Running {path_existente}...")
                        result = subprocess.run(["python", str(path_existente)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        if result.returncode == 0:  # Verificar si el script se ejecutó sin errores
                            print(result.stdout)
                            eliminar_archivos(path_estacion)  # Eliminar archivos especificados
                        else:
                            print("Error en la ejecución del script:", file=sys.stderr)
                            print(result.stderr, file=sys.stderr)
                    except Exception as e:
                        print(f"Error al ejecutar {path_existente}: {e}", file=sys.stderr)
                    print('====================================================\n')
end_time = time.time()
print(f"Tiempo total de ejecución: {end_time - start_time} segundos.")

"""
if path_existente.exists():
    # Informar que el archivo ha sido actualizado
    print('====================================================')
    print(f"File main_sql.py updated:{path_existente}")

    # Ejecutar el script actualizado
    print(f"Running {path_existente}...")
    print('====================================================')
    result = subprocess.run(["python", str(path_existente)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    print('\n')
"""
