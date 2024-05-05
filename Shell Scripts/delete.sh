# Iterar sobre cada número del 0 al 5
for j in $(seq 1 3);do
    echo "Entrando a rup_bl_$j"
    cd rup_bl_$j
    for i in $(seq 0 9); do
        # Navegar a la carpeta correspondiente
        cd "station_s$i" || continue

        # Delete useless files
        rm -f *.mpco
        rm -f *.h5drm
        rm -f *.mpco.cdata
        rm analysis_steps.tcl
        rm elements.tcl
        rm main.tcl
        rm materials.tcl
        rm nodes.tcl
        rm sections.tcl
        rm import_h5py.py

        # Results
	rm -rf Accelerations/*
	rm -rf Displacements/*
	rm -rf Reactions/*

	cd ..
    done
    cd ..
done
