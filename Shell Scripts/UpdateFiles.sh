echo "|||||||||||||||||||||||||||||||||||||"
echo "Using files from FixBase folder..."
for file in */ ; do
    cp sql_functions.py "$file"
    cp sort_results_into_xlsx.py "$file"
    cp main_sql.py "$file"
    cp accelerations_writter_tcl_format.py "$file"

    cp definitions.tcl "$file"
    #cp analysis_steps.tcl "$file"
    #cp elements.tcl "$file"
    #cp main.tcl "$file"
    #cp materials "$file"
    #cp nodes.tcl "$file"
    #cp sections.tcl "$file"

    cd "$file"
    for file2 in */ ;do
        cp sql_functions.py "$file2"
        cp sort_results_into_xlsx.py "$file2"
        cp main_sql.py "$file2"
        cp accelerations_writter_tcl_format.py "$file2"

        cp definitions.tcl "$file2"
        #cp analysis_steps.tcl "$file2"
        #cp elements.tcl "$file2"
        #cp main.tcl "$file2"
        #cp materials "$file2"
        #cp nodes.tcl "$file2"
        #cp sections.tcl "$file2"

        cd "$file2"
        for file3 in */ ;do
            cp sql_functions.py "$file3"
            cp sort_results_into_xlsx.py "$file3"
            cp main_sql.py "$file3"
            cp accelerations_writter_tcl_format.py "$file3"
            
            cp definitions.tcl "$file3"
            #cp elements.tcl "$file3"
            #cp analysis_steps.tcl "$file3"
            #cp main.tcl "$file3"
            #cp materials "$file3"
            #cp nodes.tcl "$file3"
            #cp sections.tcl "$file3"

            cd "$file3"
            rm Accelerations_writter_tcl_format.py
            rm Sort_results_into_xlsx.py
            rm SQL_functions.py
            cd ..
        done

        #rm sql_functions.py 
        #rm sort_results_into_xlsx.py 
        #rm main_sql.py
        #rm accelerations_writter_tcl_format.py
    
        #rm analysis_steps.tcl 
        rm definitions.tcl 
        #rm elements.tcl 
        #rm main.tcl 
        #rm materials 
        #rm nodes.tcl 
        #rm sections.tcl 

        cd ..

    done
    rm sql_functions.py 
    rm sort_results_into_xlsx.py 
    rm main_sql.py
    rm accelerations_writter_tcl_format.py
    
    #rm analysis_steps.tcl 
    rm definitions.tcl 
    #rm elements.tcl 
    #rm main.tcl 
    #rm materials 
    #rm nodes.tcl 
    #rm sections.tcl 

    cd ..

    
done

echo "Files updated succesfully!"
echo "|||||||||||||||||||||||||||||||||||||"
