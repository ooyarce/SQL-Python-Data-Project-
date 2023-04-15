for m_dir in m6.5 m6.7 m6.9 m7.0; do
    for rup_dir in ${m_dir}/rup_bl_1 ${m_dir}/rup_bl_2 ${m_dir}/rup_bl_3 ${m_dir}/rup_ns_1 ${m_dir}/rup_ns_2 ${m_dir}/rup_ns_3 ${m_dir}/rup_sn_1 ${m_dir}/rup_sn_2 ${m_dir}/rup_sn_3 ; do
        echo "$rup_dir"
        for station_dir in ${rup_dir}/resultado_s{0..9}; do
            if [ -d "${station_dir}/Results" ]; then
                echo "${station_dir}/Results"
            fi
        done
    done
done
