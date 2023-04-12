import subprocess
import datetime
import time

# Definir la duración del intervalo entre commits (en segundos)
intervalo = 3600

while True:
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
    print(f'Se ha realizado un commit a las {fecha_actual.strftime("%H:%M:%S")}')

    # Esperar hasta el siguiente intervalo
    tiempo_restante = intervalo
    while tiempo_restante > 0:
        print(f'Faltan {tiempo_restante//60} minutos y {tiempo_restante%60} segundos para el siguiente commit')
        tiempo_espera = min(tiempo_restante, 600)  # Esperar un máximo de 10 minutos
        time.sleep(tiempo_espera)
        tiempo_restante -= tiempo_espera
