for m_dir in station0 station1 station2 station3 station4; do
    cd "$m_dir"
        echo "Enviando a correr caso ${station_dir}"
        sbatch run.sh
	    sleep 10
    cd ..
done
