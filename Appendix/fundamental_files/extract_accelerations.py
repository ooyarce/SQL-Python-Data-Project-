import pandas as pd 
import matplotlib.pyplot as plt

def getRecordSeries(txt_file_path:str, direction:str)->pd.Series:
    """
    This function returns a Pandas Series with the acceleration data from a
    
    Parameters
    ----------
    file : str
        Path to the file with the acceleration data.
    
    Returns
    -------
    Pandas Series
        Acceleration data.
    """
    if direction not in ['n', 'e', 'z']:
        raise ValueError('Direction must be "n", "e" or "z"')
    
    with open(txt_file_path, 'r') as file:
        data = file.readlines()[1:]  # Ignorar la primera línea con metadatos
    data = [float(line.strip()) * 9.81 for line in data] #type: ignore
    dt = 0.005  # Paso de tiempo en segundos
    tiempo = [i * dt for i in range(len(data))]
    series = pd.Series(data, index=tiempo)
    
    # Determinar el intervalo de muestreo
    longitud_total = len(series)
    puntos_deseados = 2000
    intervalo = int(longitud_total / puntos_deseados)

    # Muestrear la serie cada 'intervalo' puntos
    serie_muestreada = series.iloc[::intervalo]

    # Exportar los índices y valores a archivos .txt
    serie_muestreada.index.to_series().to_csv(f'time_series_{direction}.txt', index=False, header=False)
    serie_muestreada.to_csv(f'acceleration_{direction}.txt', index=False, header=False)
    return series


txt_file_path = 'Valpo_1985_accelerations_Z.txt'
record_ss = getRecordSeries(txt_file_path, direction='z')

# Plot
plt.figure(figsize=(10, 6))
plt.plot(record_ss.index, record_ss.values)#, label='Aceleración (m/s²)')
plt.ylabel('Aceleración (m/s²)')
plt.xlabel('Tiempo (s)')
plt.title('Registro Sísmico de Valparaíso 1985')
plt.legend()
plt.grid(True)
plt.show()