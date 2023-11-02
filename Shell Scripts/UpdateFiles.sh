echo "|||||||||||||||||||||||||||||||||||||"
echo "Using files from FixBase folder..."
for file in */ ; do
    #Iterates over the magnitude (file) and gets inside when 'cd'
    #cp run_sh_writter.py "$file"
    #cp check_nodes.py "$file"
    #cp sql_functions.py "$file"
    #cp accelerations_writter_tcl_format.py "$file"
    #cp main_sql.py "$file"
    #cp exporting_results.py "$file"
    #cp sort_results_into_xlsx.py "$file"
    #cp FixBaseV55_4s.scd "$file"
    #-------------------------------
    cp ASDAbsorbingBoundary3D.tcl "$file"
    cp definitions.tcl "$file"
    cp analysis_steps.tcl "$file"
    cp elements.tcl "$file"
    cp materials.tcl "$file"
    cp main.tcl "$file"
    cp nodes.tcl "$file"
    cp sections.tcl "$file"
    cd "$file"
    for file2 in */ ;do
        #Iterates over the rupture type (file2) and gets inside when 'cd'
        #cp run_sh_writter.py "$file2"
        #cp check_nodes.py "$file2"
        #cp sql_functions.py "$file2"
        #cp accelerations_writter_tcl_format.py "$file2"
        #cp main_sql.py "$file2"
        #cp exporting_results.py "$file2"
        #cp sort_results_into_xlsx.py "$file2"
        #cp FixBaseV55_4s.scd "$file2"
        #-------------------------------
        cp ASDAbsorbingBoundary3D.tcl "$file2"
        cp definitions.tcl "$file2"
        cp analysis_steps.tcl "$file2"
        cp elements.tcl "$file2"
        cp materials.tcl "$file2"
        cp main.tcl "$file2"
        cp nodes.tcl "$file2"
        cp sections.tcl "$file2"
        cd "$file2"
        for file3 in */ ;do
            #Iterates over the station (file3) and gets inside when 'cd'
            #cp run_sh_writter.py "$file3"
            #cp check_nodes.py "$file3/Results/"
            #cp sql_functions.py "$file3"
            #cp accelerations_writter_tcl_format.py "$file3"
            #cp main_sql.py "$file3"
            #cp sort_results_into_xlsx.py "$file3"
            #cp FixBaseV55_4s.scd "$file3"
            #-------------------------------
            cp ASDAbsorbingBoundary3D.tcl "$file3"
            cp definitions.tcl "$file3"
            cp analysis_steps.tcl "$file3"
            cp elements.tcl "$file3"
            cp materials.tcl "$file3"
            cp main.tcl "$file3"
            cp nodes.tcl "$file3"
            cp sections.tcl "$file3"
            #-------------------------------
            #this WIPES INPUT
            cd "$file3"
            #rm *.log
            #rm -rf ./Displacements/*
            #rm -rf ./Reactions/*
            #rm -rf ./Accelerations/*
            #rm -rf ./Results/accel/
            #rm -rf ./Results/coords
            #rm -rf ./Results/disp/
            #rm -rf ./Results/info/
            #rm -rf ./Results/reaction/
            #rm FixBaseV55_2s.scd 
            cd ..
            #-------------------------------
        done
        #rm run_sh_writter.py
        #rm check_nodes.py
        #rm sql_functions.py 
        #rm accelerations_writter_tcl_format.py
        #rm main_sql.py
        #rm sort_results_into_xlsx.py 
        #rm FixBaseV55_4s.scd
        #rm exporting_results.py
        #-------------------------------
        rm ASDAbsorbingBoundary3D.tcl
        rm definitions.tcl 
        rm analysis_steps.tcl 
        rm elements.tcl 
        rm materials.tcl 
        rm main.tcl 
        rm nodes.tcl 
        rm sections.tcl 
        cd ..
    done
    #rm run_sh_writter.py 
    #rm check_nodes.py
    #rm sql_functions.py
    #rm accelerations_writter_tcl_format.py
    #rm main_sql.py
    #rm sort_results_into_xlsx.py 
    #rm FixBaseV55_4s.scd
    #-------------------------------
    rm ASDAbsorbingBoundary3D.tcl
    rm definitions.tcl
    rm analysis_steps.tcl 
    rm elements.tcl 
    rm materials.tcl 
    rm main.tcl 
    rm nodes.tcl 
    rm sections.tcl 
    cd ..
done
echo "Files updated succesfully!"
echo "|||||||||||||||||||||||||||||||||||||"
