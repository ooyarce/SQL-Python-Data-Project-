#!/bin/bash

# Iterar sobre cada número del 0 al 5
iter = 1
for i in $(seq 0 2); do
    # Copiar archivo a carpeta
    #cp import_h5py.py "station_s$i" 
    
    # Navegar a la carpeta correspondiente
    cd "station_s$i" || continue

    # Crear arcceso directo para archivo h5drm
    comando="ln -sf /mnt/krakenschest/home/FSR_DRM_Motions/m6.7_rup_bl_1_motions_sta_$i.h5drm input.h5drm"
    eval $comando

    # Correr archivo generador de input
    python3 import_h5py.py

    # Correr el archivo
    sbatch run.sh
    
    # Volver al directorio principal
    cd ..
    
    # Imprimir el mensaje indicando la ejecución
    echo "se ejecutó el comando $comando en la carpeta station$i"
done
