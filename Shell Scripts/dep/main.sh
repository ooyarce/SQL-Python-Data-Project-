#sh UpdateFiles.sh
for file in */ ; do
    cd "$file"
    for file2 in */ ;do
        cd "$file2"
        echo "\n|--------------------------------------------------------|"
        echo "|\t\tRunning case: $file$file2 \t\t |"
        echo "|--------------------------------------------------------|"
        for file3 in */ ;do
            echo "\n|--------------------------------------------------------|"
            echo "|\t\tRunning case: $file3  \t\t |"
            echo "|--------------------------------------------------------|"
            cd "$file3"
            python3 main_sql.py
            cd ..
        done
        cd ..
    done
    cd ..
done
