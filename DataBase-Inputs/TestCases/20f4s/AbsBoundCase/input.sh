#!/bin/bash

# Iterar sobre cada número del 0 al 5
for j in $(seq 1 3);do
    for i in $(seq 0 2); do
        # Copy config
        cp run.sh                     "rup_bl_$j/station_s$i"
        cp timeSeries.txt             "rup_bl_$j/station_s$i"
        cp import_h5py.py             "rup_bl_$j/station_s$i" 

        # Copy input
        echo "Deleting folders..."
	    rm -rf "rup_bl_$j/station_s$i/Accelerations"
        rm -rf "rup_bl_$j/station_s$i/Displacements"
        rm -rf "rup_bl_$j/station_s$i/PartitionsInfo"

        echo "Copying folders and replacing new files"
	    cp -r Accelerations           "rup_bl_$j/station_s$i"
        cp -r Displacements           "rup_bl_$j/station_s$i"
        cp -r PartitionsInfo          "rup_bl_$j/station_s$i"
        cp analysis_steps.tcl         "rup_bl_$j/station_s$i"
        cp ASDAbsorbingBoundary3D.tcl "rup_bl_$j/station_s$i"
        cp definitions.tcl            "rup_bl_$j/station_s$i"
        cp elements.tcl               "rup_bl_$j/station_s$i"
        cp main.tcl                   "rup_bl_$j/station_s$i"
        cp materials.tcl              "rup_bl_$j/station_s$i"
        cp nodes.tcl                  "rup_bl_$j/station_s$i"
        cp sections.tcl               "rup_bl_$j/station_s$i"
    done
done

for j in $(seq 1 3);do
    echo "Entrando a rup_bl_$j"
    cd rup_bl_$j
    for i in $(seq 0 2); do
        # Navegar a la carpeta correspondiente
        cd "station_s$i" || continue

        # Crear arcceso directo para archivo h5drm
        comando="ln -sf /mnt/krakenschest/home/FSR_DRM_Motions/m6.7_rup_bl_${j}_motions_sta_$i.h5drm input.h5drm"
        eval $comando

        # Correr archivo generador de input
        python3 import_h5py.py

        # Correr el archivo
        sbatch run.sh
        
        # Imprimir el mensaje indicando la ejecución
        echo "Command: $comando executed in station$i folder"

        # Salir del station
        cd ..
    done

    # Salir del rup_type
    cd ..
done
