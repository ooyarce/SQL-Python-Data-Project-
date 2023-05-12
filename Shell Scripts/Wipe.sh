i=42029
while [ $i -le 42118 ]
do
  scancel $i
  i=$((i+1))
done
