for m_dir in station0 station1 station2 station3 station4; do
    cd "$m_dir"
        cd "$station_dir"
        echo "Enviando a correr caso ${m_dir}/${rup_dir}/${station_dir}"
        sbatch run.sh
	    sleep 10
            cd ..
        done
        cd ..
    done
    cd ..
done
