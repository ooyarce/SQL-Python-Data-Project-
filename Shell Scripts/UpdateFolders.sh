for m_dir in m6.5 m6.7 m6.9 m7.0; do
    for rup_dir in ${m_dir}/rup_bl_1 ${m_dir}/rup_bl_2 ${m_dir}/rup_bl_3 ${m_dir}/rup_ns_1 ${m_dir}/rup_ns_2 ${m_dir}/rup_ns_3 ${m_dir}/rup_sn_1 ${m_dir}/rup_sn_2 ${m_dir}/rup_sn_3 ; do
        for station_dir in ${rup_dir}/resultado_s0 ${rup_dir}/resultado_s1 ${rup_dir}/resultado_s2 ${rup_dir}/resultado_s3 ${rup_dir}/resultado_s4 ${rup_dir}/resultado_s5 ${rup_dir}/resultado_s6 ${rup_dir}/resultado_s7 ${rup_dir}/resultado_s8 ${rup_dir}/resultado_s9 ; do
        #mkdir "${station_dir}/Results"
	    if [ -d "${station_dir}/Results" ]; then
                cp -r accel "${station_dir}/Results"
                cp -r coords "${station_dir}/Results"
                cp -r disp "${station_dir}/Results"
                cp -r info "${station_dir}/Results"
                cp -r reaction "${station_dir}/Results"
            fi
        done
    done
done
