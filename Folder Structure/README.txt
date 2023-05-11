Primero que todo, debes pegar los input files de tu modelo base en la carpeta de este README.txt
Segundo, correr el archivo que creará los 360 modelos mediante el comando:
sh Input_sort_results.sh

Lo que hará ese código es crear y poner en el modelo los inputs generados pertenecientes a los archivos .npz de shakermaker.
Una vez corrido este archivo, debes copiar toda la carpeta hacia el clúster y de ahí correr el archivo RunModels.sh mediante el código
sh RunModels.sh

Luego a esperar; los resultados estaŕán de manera ordenada en cada carpeta con el formato resultado_si, que implica los resultados en la estación "i" para un tipo de ruptura determinada
y para una magnitud específica. La falla se localiza en la mitad.

Ahora lo que hay que hacer es ver la forma en que se pueden automatizar los resultados del corte basal y el drift entre pisos.

Primero Write_definitions.py => se cambia las timeseries en definitions por el input de shakermaker para el UniformExcitation
correr modelos en clúster
Segundo Sort_results_into_xlsx.py => se generan 3 archivos excel con los resultados de reacciones, desplazamientos y acceleraciones
Tercero Main_SQL.py => se generan todas las querys para ingresas los resultados de manera correcta a la base de datos.
