import logging
import subprocess
import datetime
import time

# Configurar el registro de salida
logging.basicConfig(filename='github_uploads.log', level=logging.INFO)
fecha_actual = datetime.datetime.now()
logging.info(f'SESION INICIADA el {fecha_actual.strftime("%d/%m/%Y a las %H:%M:%S")}')

# Definir la duración del intervalo entre commits (en segundos)
intervalo = 600

while True:
    # Esperar hasta el siguiente intervalo
    tiempo_restante = intervalo
    while tiempo_restante > 0:
        #logging.info(f'Faltan {tiempo_restante//60} minutos para el siguiente commit')
        tiempo_espera = min(tiempo_restante, 60)  # Esperar un máximo de 1 minutos
        time.sleep(tiempo_espera)
        tiempo_restante -= tiempo_espera
        
    # Ejecutar el comando 'git add .'
    subprocess.run(['git', 'add', '.'])

    # Generar el mensaje de commit con la fecha y hora actual
    fecha_actual = datetime.datetime.now()
    mensaje_commit = f'Commit realizado el {fecha_actual.strftime("%d/%m/%Y a las %H:%M:%S")}'

    # Ejecutar el comando 'git commit'
    subprocess.run(['git', 'commit', '-m', mensaje_commit])

    # Ejecutar el comando 'git push'
    subprocess.run(['git', 'push'])
    
    # Imprimir mensaje de confirmación
    logging.info(f'Se ha realizado un commit a las {fecha_actual.strftime("%H:%M:%S")}')

