i=49845
while [ $i -le 50051 ]
do
  scancel $i
  i=$((i+1))
done
