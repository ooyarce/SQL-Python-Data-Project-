# Iterar sobre cada número del 0 al 5
for j in $(seq 1 2);do
    echo "Entrando a rup_bl_$j"
    cd rup_bl_$j
    for i in $(seq 3 9); do
        # Navegar a la carpeta correspondiente
        cd "station_s$i" || continue

        # Delete useless files
        rm -f *.mpco
        rm -f *.h5drm
        cd ..
    done
    cd ..
done