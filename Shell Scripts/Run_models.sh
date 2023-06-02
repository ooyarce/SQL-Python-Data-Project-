for m_dir in m6.5 m6.7 m6.9 m7.0; do
	cd "$m_dir"
	for rup_dir in rup_bl_1 rup_bl_2 rup_bl_3 rup_ns_1 rup_ns_2 rup_ns_3 rup_sn_1 rup_sn_2 rup_sn_3 ; do
		cd "$rup_dir"
		for station_dir in resultado_s0 resultado_s1 resultado_s2 resultado_s3 resultado_s4 resultado_s5 resultado_s6 resultado_s7 resultado_s8 resultado_s9 ; do
			cd "$station_dir"
			echo "\n|--------------------------------------------------------|"
            echo "|\t\tRunning case: $m_dir$rup_dir$station_dir|"
            echo "|--------------------------------------------------------|"
			sbatch run.sh
			sleep 10
			cd ..
		done
		cd ..
	done
	cd ..
done
