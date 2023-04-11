#sh UpdateFiles.sh
for file in */ ; do
    cd "$file"
    for file2 in */ ;do
        cd "$file2"
        echo "\n|--------------------------------------------------------|"
        echo "|\t\tRunning case: $file$file2 \t\t |"
        echo "|--------------------------------------------------------|"
        python3 exporting_results.py
        mv resultado_s0*.txt resultado_s0/
        mv resultado_s1*.txt resultado_s1/
        mv resultado_s2*.txt resultado_s2/
        mv resultado_s3*.txt resultado_s3/
        mv resultado_s4*.txt resultado_s4/
        mv resultado_s5*.txt resultado_s5/
        mv resultado_s6*.txt resultado_s6/
        mv resultado_s7*.txt resultado_s7/
        mv resultado_s8*.txt resultado_s8/
        mv resultado_s9*.txt resultado_s9/
        for file3 in */ ;do
            cd "$file3"
            python3 accelerations_writter_tcl_format.py
            mv definitions.tcl definitions_old.tcl
            mv definitions2.tcl definitions.tcl
            rm tcl_format_east.tcl
            rm tcl_format_north.tcl
            rm tcl_format_vertical.tcl 
            cd ..
        done
        cd ..
    done
    cd ..
done
