#!/bin/bash

# Iterar sobre cada número del 0 al 5
for i in $(seq 0 5); do
    # Copiar archivo a carpeta
    cp import_h5py.py "station$i" 
    
    # Navegar a la carpeta correspondiente
    cd "station$i" || continue

    # Crear arcceso directo para archivo h5drm
    comando="ln -sf /mnt/krakenschest/home/FSR_DRM_Motions/m6.50_rup_bl_1_motions_sta_$i.h5drm input.h5drm"
    eval $comando

    # Correr archivo generador de input
    python3 import_h5py.py

    # Volver al directorio principal
    cd ..
    
    # Imprimir el mensaje indicando la ejecución
    echo "se ejecutó el comando $comando en la carpeta station$i"
done
