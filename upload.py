import subprocess
import datetime

# Ejecutar el comando 'git add .'
subprocess.run(['git', 'add', '.'])

# Generar el mensaje de commit con la fecha y hora actual
fecha_actual = datetime.datetime.now()
mensaje_commit = f'Commit realizado el {fecha_actual.strftime("%d/%m/%Y a las %H:%M:%S")}'

# Ejecutar el comando 'git commit'
subprocess.run(['git', 'commit', '-m', mensaje_commit])

# Ejecutar el comando 'git push'
subprocess.run(['git', 'push'])
