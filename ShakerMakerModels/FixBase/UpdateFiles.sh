echo "|||||||||||||||||||||||||||||||||||||"
echo "Using files from FixBase folder..."
for file in */ ; do
    #Iterates over the magnitude (file) and gets inside when 'cd'

    #cp run.sh "$file"
    #cp accelerations_writter_tcl_format.py "$file"
    #cp sort_results_into_xlsx.py "$file"
    #cp definitions.tcl "$file"
    #cp sql_functions.py "$file"
    #cp exporting_results.py "$file"
    #cp check_nodes.py "$file"

    #cp analysis_steps.tcl "$file"
    #cp elements.tcl "$file"
    #cp main.tcl "$file"
    #cp materials "$file"
    #cp nodes.tcl "$file"
    #cp sections.tcl "$file"

    cd "$file"
    for file2 in */ ;do
        #Iterates over the rupture type (file2) and gets inside when 'cd'

        #cp accelerations_writter_tcl_format.py "$file2"
        #cp sort_results_into_xlsx.py "$file2"
        #cp definitions.tcl "$file2"
        #cp sql_functions.py "$file2"
        #cp exporting_results.py "$file2"
        #cp check_nodes.py "$file2"


        #cp analysis_steps.tcl "$file2"
        #cp elements.tcl "$file2"
        #cp main.tcl "$file2"
        #cp materials "$file2"
        #cp nodes.tcl "$file2"
        #cp sections.tcl "$file2"

        cd "$file2"
        for file3 in */ ;do
            #Iterates over the station and gets inside when 'cd'

            #cp accelerations_writter_tcl_format.py "$file3"
            #cp sort_results_into_xlsx.py "$file3"
            #cp sql_functions.py "$file3"
            #cp check_nodes.py "$file3/Results/"

            #cp definitions.tcl "$file3"
            #cp elements.tcl "$file3"
            #cp analysis_steps.tcl "$file3"
            #cp main.tcl "$file3"
            #cp materials "$file3"
            #cp nodes.tcl "$file3"
            #cp sections.tcl "$file3"

            cd "$file3"
            #rm check_nodes.py
            cd ..
        done

        #rm check_nodes.py
        #rm sql_functions.py 
        #rm accelerations_writter_tcl_format.py
        #rm sort_results_into_xlsx.py 
        #rm definitions.tcl 

        #rm analysis_steps.tcl 
        #rm elements.tcl 
        #rm main.tcl 
        #rm materials 
        #rm nodes.tcl 
        #rm sections.tcl 

        cd ..

    done

    #rm accelerations_writter_tcl_format.py
    #rm sort_results_into_xlsx.py 
    #rm sql_functions.py 
    #rm exporting_results.py
    #rm check_nodes.py
    #rm definitions.tcl
    #rm analysis_steps.tcl 
    #rm elements.tcl 
    #rm main.tcl 
    #rm materials 
    #rm nodes.tcl 
    #rm sections.tcl 

    cd ..

    
done

echo "Files updated succesfully!"
echo "|||||||||||||||||||||||||||||||||||||"
