#sh UpdateFiles.sh
for file in */ ; do
    cd "$file"
    for file2 in */ ;do
        cd "$file2"
        echo "\n|--------------------------------------------------------|"
        echo "|\t\tRunning case: $file$file2 \t\t |"
        echo "|--------------------------------------------------------|"
        for file3 in */ ;do
            cd "$file3"
            python3 sort_results_into_xlsx.py
            cd ..
        done
        cd ..
    done
    cd ..
done
