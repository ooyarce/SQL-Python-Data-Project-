import h5py
import pandas as pd
import numpy as np

def computeInputFromH5DRMFile(input_type, input = 'input.h5drm'):
    """
    This function computes the input from the H5DRM file and writes each column (X, Y, Z)
    to a separate text file.

    Parameters
    ----------
    input_type : str
        Input type. It must be 'acceleration', 'displacement', or 'velocity'.

    return
    ------
    text files with the input data (3, 1 for each direction)
    """
    ids = ['e', 'n', 'z']
    with h5py.File(input, 'r') as f:
        dataset_path = f'DRM_QA_Data/{input_type}'
        if dataset_path in f:
            dataset = f[dataset_path]
            data = dataset[:, :16000]

            # Convierte los datos a un DataFrame de Pandas
            df = pd.DataFrame(data.T, columns=['X', 'Y', 'Z'])

            for i,col in enumerate(df.columns):
                output_file = f'{input_type}_{ids[i]}.txt'
                with open(output_file, 'w') as file:
                    for item in df[col]:
                        file.write(f"{item}\n")
                print(f'Archivo {output_file} creado con éxito.')

            #NOTE:DEPRECATED LINE, ADD ONLY IF YOU WANNA INCLUDE IT IN THE DT COLUMN
            # Agrega la columna "DT" al inicio del DataFrame
            #time_array = np.arange(start_time, end_time + step_time, step_time)[:16000]
            #df.insert(0, 'DT', time_array)

        else:
            print(f"El conjunto de datos {dataset_path} no se encuentra en el archivo.")
computeInputFromH5DRMFile('acceleration')
computeInputFromH5DRMFile('velocity')