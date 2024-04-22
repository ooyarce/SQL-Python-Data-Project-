# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
from pyseestko.errors import NCh433Error, DataBaseError
from pathlib          import Path
from typing           import List

from shutil           import SameFileError
import numpy          as np
import importlib.util
import subprocess
import logging
import shutil
import time
import math
import sys
import re




# ==================================================================================
# =============================== GETTERS FUNCTIONS ================================
# ==================================================================================
def mapSimTypeID(sim_type):
    simulation_type_dict = {'FixBase': 1,'AbsBound': 2,'DRM': 3,}
    st = simulation_type_dict.get(sim_type, None)
    if st is None:
        raise Exception(f"Unrecognized simulation type '{sim_type}'.\n"
                        "Valid simulation types are 'FixBase', 'AbsBound', and 'DRM'.\n"
                        "Please check that the 'Path' and 'Folder Names' are correct.")
    return st

def getModelKeys(project_path):
    sim_type = project_path.parents[3].parent.name

    mag      = project_path.parents[2].name[1:]
    if mag not in ['6.5', '6.7', '6.9', '7.0']:
        raise Exception(f"Unrecognized magnitude '{mag}'.\n"
                        "Valid magnitudes are '6.5', '6.7', '6.9', and '7.0'.\n"
                        "Please check that the 'Path' and 'Folder Names' are correct.")

    rup      = project_path.parents[1].name[4:6]
    if rup not in ['bl', 'ns', 'sn']:
        raise Exception(f"Unrecognized rupture type '{rup}'.\n"
                        "Valid rupture types are 'bl', 'ns', and 'sn'.\n"
                        "Please check that the 'Path' and 'Folder Names' are correct.")

    # Extraer y validar la iteración
    iter_name = project_path.parents[1].name
    match = re.search(r"_(\d+)$", iter_name)
    if not match:
        raise Exception("No iteration number found in the folder name.")
    iter = int(match.group(1))
    if iter not in range(1, 11):
        raise Exception(f"Unrecognized iteration '{iter}'.\n"
                        "Valid iterations are from 1 to 10.\n"
                        "Please check that the 'Path' and 'Folder Names' are correct.")

    station = project_path.parent.name[-2:]
    if station not in ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9']:
        raise Exception(f"Unrecognized station '{station}'.\n"
                        "Valid stations are 's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', and 's9'.\n"
                        "Please check that the 'Path' and 'Folder Names' are correct.")
    return sim_type, mag, rup, iter, station

def getBoxParams(sim_type, sim_keys):
    box_comments  = f'Box: {sim_keys}'                    if sim_type != 1 else f'No Box: {sim_keys}'
    soil_mat_name = 'Elastoisotropic'                     if sim_type != 1 else 'No Soil material'
    soil_ele_type = 'SSPBrick Element'                    if sim_type != 1 else 'No Soil element'
    mesh_struct   = 'Structured Quad Elem by 1.25 meters' if sim_type != 1 else 'No Soil mesh'
    vs30          = '750 m/s'                             if sim_type != 1 else 'No Vs30'
    soil_dim      = '3D'                                  if sim_type != 1 else 'No Soil dimension'
    return box_comments, soil_mat_name, soil_ele_type, mesh_struct, vs30, soil_dim

def get_mappings():
    magnitude_mapping = {
        0.0: "Not defined",
        6.5: "6.5 Mw",
        6.7: "6.7 Mw",
        6.9: "6.9 Mw",
        7.0: "7.0 Mw"}

    location_mapping = {
        -1: 'Not defined',
        0: "UAndes Campus",
        1: "Near field North",
        2: "Near field Center",
        3: "Near field South",
        4: "Intermediate field North",
        5: "Intermediate field Center",
        6: "Intermediate field South",
        7: "Far field North",
        8: "Far field Center",
        9: "Far field South"}

    ruptures_mapping = {
        0: "Not defined",
        1: "Bilateral",
        2: "North-South",
        3: "South-North"}
    return magnitude_mapping, location_mapping, ruptures_mapping





# ==================================================================================
# =============================== UTILITY FUNCTIONS ================================
# ==================================================================================
def load_module(module_name, module_path):
    """
    To use it you have to do something like this:

    # Rutas completas a los módulos que deseas importar
    path_to_post_processing = "C:/workspace/AndesLab/AnDeS_23/pyandes_23/processing/post_processing.py"
    path_to_etabs21_geo = "C:/workspace/AndesLab/AnDeS_23/pyandes_23/processing/etabs21_geo.py"

    # Cargar los módulos
    prs = load_module("post_processing", path_to_post_processing)
    etabs_geo = load_module("etabs21_geo", path_to_etabs21_geo)
    """
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        print(f"No se pudo cargar el módulo: {module_name}")
        return None

def setup_logger(verbose, module_name):
    logger = logging.getLogger(module_name)
    handler = logging.StreamHandler()

    # Si verbose es 0, no se imprime nada
    if verbose == 0:
        logger.addHandler(logging.NullHandler())
        return logger


    # Define los formatters
    formatter_level_1 = logging.Formatter('%(levelname)s: %(message)s')  # Nivel 1
    formatter_level_2 = logging.Formatter('%(name)s - %(levelname)s: %(message)s')  # Nivel 2
    formatter_level_3 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                          '%Y-%m-%d %H:%M:%S')  # Nivel 3

    # Ajusta formatter y nivel basado en verbose
    if verbose == 1:
        handler.setFormatter(formatter_level_1)
        logger.setLevel(logging.INFO)
    elif verbose == 2:
        handler.setFormatter(formatter_level_2)
        logger.setLevel(logging.INFO)
    elif verbose >= 3:
        handler.setFormatter(formatter_level_3)
        logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger

def initialize_ssh_tunnel(server_alive_interval=60):
    """
    This function initializes an SSH tunnel to the Kraken server. If the tunnel is already established, the function
    will check if the SSH process is running. If the process is not running, the function will close all existing SSH
    processes and attempt to restart the tunnel.
    
    Parameters:
    -----------
    server_alive_interval: int
        The interval in seconds to send a keepalive message to the server. The default value is 60 seconds.
        
    Raises:
    -------
    DataBaseError:
        If an error occurs while trying to open the cmd.
    """
    local_port = "3306"
    try:
        # Ejecutar netstat y capturar la salida con una codificación adecuada
        netstat_output = subprocess.check_output(['netstat', '-ano'], text=True, encoding='cp1252')

        # Buscar el puerto local en la salida de netstat
        if re.search(rf'\b{local_port}\b', netstat_output):
            print("SSH tunnel already established and operational...")

            # Verificar si el proceso SSH está activo usando tasklist
            tasklist_output = subprocess.check_output(['tasklist'], text=True, encoding='cp1252')
            if "ssh.exe" in tasklist_output:
                print("SSH process is running.")
            else:
                print("SSH process not running. Closing all existing SSH processes and attempting to restart...")
                # Cerrar todos los procesos SSH
                subprocess.call(["taskkill", "/F", "/IM", "ssh.exe"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                # Cerrar el túnel existente y abrir uno nuevo
                command = f"ssh -o ServerAliveInterval={server_alive_interval} -L 3306:localhost:3307 cluster ssh -L 3307:kraken:3306 kraken"
                subprocess.call(["cmd.exe", "/c", "start", "/min", "cmd.exe", "/k", command])

        else:
            # Si el puerto local no está en uso, abrir el túnel
            print("Attempting to establish the SSH Tunnel...")
            command = f"ssh -o ServerAliveInterval={server_alive_interval} -L 3306:localhost:3307 cluster ssh -L 3307:kraken:3306 kraken"
            subprocess.call(["cmd.exe", "/c", "start", "/min", "cmd.exe", "/k", command])

    except subprocess.CalledProcessError as e:
        raise DataBaseError(f"Error executing a system command: {e}")
    except Exception as e:
        raise DataBaseError(f"Error trying to open cmd: {e}")


def folder_size(path:Path, folder_name:str):
    """
    This function calculates the size of a folder in bytes.
    
    Parameters:
    -----------
    path: Path
        The path where the folder is located.
    folder_name: str
        The name of the folder to calculate the size.
        
    Returns:
    --------
    int:
        The size of the folder in bytes.
    """
    folder_path = path / folder_name
    return sum(file.stat().st_size for file in folder_path.iterdir() if file.is_file())

def single_sim_files_to_delete(
    path:Path, 
    files_to_delete:list=["analysis_steps.tcl",
                         "elements.tcl",
                         "main.tcl",
                         "materials.tcl",
                         "nodes.tcl",
                         "sections.tcl",
                         "*.mpco",
                         "*.mpco.cdata",
                         "import_h5py.py",
                         "input.h5drm"]
    )-> None:
    """
    This function deletes the files specified in the list files_to_delete
    in the path specified. If the files are not found, the function will
    print a message indicating that the files are not found.
    
    Parameters:
    -----------
    path: Path
        The path where the files are located.
    files_to_delete: list
        A list of strings with the files to delete. The function will
        use the glob function to find the files to delete.
    """
    for file in files_to_delete:
        for file_path in path.glob(file):
            try:
                file_path.unlink()
                print(f"File {file_path} succesfully deleted.")
            except Exception as e:
                print(f"Files already deleted or non existant in {file_path}: {e}")

def run_main_sql_simulations(
    root_path         : Path,
    new_main_sql_path : Path,
    sim_types         : List[str],
    structure_types   : List[str],
    rupture_iters     : List[int],
    stations          : List[str],
    files_to_delete    :list=[
                        "analysis_steps.tcl",
                        "elements.tcl",
                        "main.tcl",
                        "materials.tcl",
                        "nodes.tcl",
                        "sections.tcl",
                        "*.mpco",
                        "*.mpco.cdata",
                        "import_h5py.py",
                        "input.h5drm"]
    ) -> None:
    """
    This function updates the main_sql.py file in the specified path and runs the simulation
    for each simulation type, structure type, rupture iteration, and station specified. If the
    simulation is executed successfully, the function will delete the files specified in the
    single_sim_files_to_delete function.
    
    Parameters:
    -----------
    root_path: Path
        The root path where the simulation folders are located. 
    new_main_sql_path: Path
        The path to the new main_sql.py file that will be copied to the simulation folders. If
        None, then the function will not update the main_sql.py file.
    sim_types: List[str]
        A list of strings with the simulation types. The function will iterate over each
        simulation type in the list.
    structure_types: List[str]
        A list of strings with the structure types. The function will iterate over each
        structure type in the list.
    rupture_iters: List[int]
        A list of integers with the rupture iterations. The function will iterate over each
        rupture iteration in the list.
    stations: List[str]
        A list of strings with the stations. The function will iterate over each station in
        the list.
    """
    # Start the timer to measure the execution time
    start_time = time.time()
    
    # Iterate over each simulation type
    for sim_type in sim_types:
        
        # Iterate over each structure type inside the simulation type folder
        for structure in structure_types:
            magnitude = 'm6.7'
            path_to_magnitude =  root_path / sim_type / structure / magnitude
            if not path_to_magnitude.exists():
                continue
            
            # Iterate over each rupture type inside the magnitude folder
            for rup_iter in rupture_iters:
                rup = f'rup_bl_{rup_iter}'
                rup_path = path_to_magnitude / rup
                if not rup_path.exists():
                    continue
                
                # Iterate over each station inside the rupture type folder
                for station in stations:
                    path_to_station = rup_path / station
                    if not path_to_station.exists():
                        continue

                    # Copy the new main_sql.py file to the station folder
                    path_to_paste = path_to_station / "main_sql.py"
                    if new_main_sql_path is not None:
                        copy_paste_file(new_main_sql_path, path_to_paste)

                    # Try to run the main_sql.py file in the station folder and delete the files specified
                    try:
                        print(f"Running {path_to_paste}...")
                        result = subprocess.run(["python", str(path_to_paste)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        if result.returncode == 0:  # Verify if the script was executed successfully
                            print(result.stdout)
                            single_sim_files_to_delete(path_to_station, files_to_delete)  # Delete the files specified in the function
                        else:
                            print("Error in python code:", file=sys.stderr)
                            print(result.stderr, file=sys.stderr)
                    except Exception as e:
                        print(f"Error executing {path_to_paste}: {e}", file=sys.stderr)
                    print('====================================================\n')
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time} seconds.")

def copy_paste_file(origin:Path, destination:Path):
    """
    This function copies the file specified in the origin path to the destination path.
    """
    try:
        shutil.copy(origin, destination)
    except SameFileError:
        print(f'File: {origin}\nIs the same as:\n {destination}.\nSkipping copy...')
    # Print that the file was updated
    print('====================================================')
    print(f"File main_sql.py updated in {destination}")


# ==================================================================================
# ================================ MATH FUNCTIONS ==================================
# ==================================================================================
def pwl(vector_a, w, chi,step=0.04):
    """
    Use step = 0.04 for 1000 values
    Use step = 0.02 for 2000 values
    Use step = 0.01 for 4000 values
    Use step = 0.005 for 8000 values
    Use step = 0.0025 for 16000 values
    """
    # Precompute constants
    h = step
    m = 1
    w_d = w * np.sqrt(1 - chi**2)  # 1/s

    # Define functions
    sin = np.sin(w_d * h)
    cos = np.cos(w_d * h)
    e = np.exp(-chi * w * h)
    raiz = np.sqrt(1 - chi**2)
    division = 2 * chi / (w * h)

    A = e * (chi * sin / raiz + cos)
    B = e * (sin / w_d)
    C = (1 / w**2) * (division + e * (((1 - (2 * chi**2)) / (w_d * h) - chi / raiz) * sin - (1 + division) * cos))
    D = (1 / w**2) * (1 - division + e * ((2 * chi**2 - 1) * sin / (w_d * h) + division * cos))

    A1 = -e * ((w * sin) / raiz)
    B1 = e * (cos - chi * sin / raiz)
    C1 = (1 / w**2) * (-1 / h + e * ((w / raiz + chi / (h * raiz)) * sin + cos / h))
    D1 = (1 / w**2) * (1 / h - (e / h * (chi * sin / raiz + cos)))

    # Initialize vectors
    u_t = np.zeros(len(vector_a))
    up_t = np.zeros(len(vector_a))

    # Compute the first two values of the vectors
    for i in range(len(vector_a) - 1):
        pi = -vector_a[i] * m
        pi1 = -vector_a[i + 1] * m

        ui = u_t[i]
        vi = up_t[i]

        u_t[i + 1] = A * ui + B * vi + C * pi + D * pi1
        up_t[i + 1] = A1 * ui + B1 * vi + C1 * pi + D1 * pi1
    return u_t, up_t




# ==================================================================================
# ================================ UTILITY CLASSES =================================
# ==================================================================================
class NCh433_2012:
    # ===================================================
    # INIT PARAMETERS
    # ===================================================
    def __init__(self, zone, soil_category, importance):
        # Parameters
        self.zone          = self.getSeismicZone_c4_1(zone) # (1,2,3)
        self.soil_category = soil_category # (1,2,3,4)
        self.importance    = importance # UPDATE: A, B, C, D, E. Deprecated: (1,2,3,4)
        self.g  = 9.81 # m/s2
        self.R  = 7.0 # R factor from table 5.1
        self.Ro = 11.0 # Ro factor from table 5.1 
        
        
        
        
    # ===================================================
    # INITIAL METHODS TO GET THE CONSTRUCTOR PARAMETERS
    # ===================================================
    @staticmethod
    def getSeismicZone_c4_1(loc):
        citiesZone1 = set(["Curarrehue", "Lonquimay", "Melipeuco", "Pucon"])
        citiesZone2 = set(["Calle Larga", "Los Andes", "San Esteban", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia",
                       "Colina", "Conchali", "El Bosque", "Estacion Central", "Huechuraba", "Independencia",
                       "Isla de Maipo", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Las Condes",
                       "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipu", "Ñuñoa", "Padre Hurtado", "Paine",
                       "Pedro Aguirre Cerda" "Peñaflor", "Peñalolen", "Pirque", "Providencia", "Pudahuel", "Puente Alto",
                       "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquin", "San Jose de Maipo",
                       "San Miguel", "San Ramon", "Santiago", "Talagante", "Vitacura", "Chepica", "Chimbarongo", "Codegua",
                       "Coinco", "Coltauco", "Doñihue", "Graneros", "Machali", "Malloa", "Mostazal", "Nancagua", "Olivar",
                       "Placilla", "Quinta de Tilcoco", "Rancagua", "Rengo", "Requinoa", "San Fernando", "San Vicente de Tagua Tagua",
                       "Colbun", "Curico", "Linares", "Longavi", "Molina", "Parral", "Pelarco", "Rauco", "Retiro",
                       "Rio Claro", "Romeral", "Sagrada Familia", "San Clemenete", "San Rafael", "Teno", "Villa Alegre",
                       "Yerbas Buenas", "Antuco", "Coihueco", "El Carmen", "Los Angeles", "Mulchen", "Ñiquen", "Pemuco",
                       "Penco", "Quilaco", "Quilleco", "San Fabian", "San Ignacio", "Santa Barbara", "Tucapel", "Yungay",
                       "Collipulli", "Cunco", "Curacautin", "Ercilla", "Freire", "Gorbea", "Lautaro", "Loncoche",
                       "Perquenco", "Pitrufquen", "Temuco", "Victoria", "Vilcun", "Villarrica"])
        citiesZone3 = set(["Andacollo", "Combarbala", "Coquimbo", "Illapel", "La Higuera", "La Serena", "Los Vilos", "Canela",
                       "Monte Patria", "Ovalle", "Paiguano", "Punitaqui", "Rio Hurtado", "Salamanca", "Vicuña",
                       "Algarrobo", "Cabildo", "Calera", "Cartagena", "Casablanca", "Catemu", "Concon", "El Quisco",
                       "El Tabo", "Hijuelas", "La Cruz", "La Ligua", "Limache", "Llayllay", "Nogales", "Olmue", "Panquehue",
                       "Papudo", "Petorca", "Puchuncavi", "Putaendo", "Quillota", "Quilpue", "Quintero", "Rinconada",
                       "San Antonio", "San Felipe", "Santa Maria", "Santo Domingo", "Valparaiso", "Villa Alemana",
                       "Viña del Mar", "Zapallar", "Alhue", "Curacavi", "El Monte", "Lampa", "Maria Pinto", "Melipilla",
                       "San Pedro", "TilTil", "La Estrella", "Las Cabras", "Litueche", "Lolol", "Marchihue", "Navidad",
                       "Palmilla", "Peralillo", "Paredones", "Peumo", "Pichidegua", "Pichilemu", "Pumanque", "Santa Cruz",
                       "Cauquenes", "Chanco", "Constitucion", "Curepto", "Empedrado","Licanten", "Maule", "Pelluhue",
                       "Pencahue", "San Javier", "Talca", "Vichuquen", "Alto Bio Bio", "Arauco", "Bulnes", "Cabrero",
                       "Cañete", "Chiguayante", "Chillan", "Chillan Viejo", "Cobquecura", "Coelemu", "Contulmo", "Coronel",
                       "Curanilahue", "Florida", "Hualpen", "Hualqui", "Laja", "Lebu", "Los Alamos", "Lota", "Nacimiento",
                       "Negrete", "Ninhue", "Pinto", "Portezuelo", "Quillon", "Quirihue", "Ranquil", "San Carlos",
                       "San Nicolas", "San Pedro de la Paz", "San Rosendo", "Santa Juana", "Talcahuano", "Tirua", "Tome",
                       "Treguaco", "Yumbel", "Angol", "Carahue", "Cholchol", "Galvarino", "Los Sauces", "Lumaco",
                       "Nueva Imperial", "Padre Las Casas", "Puren", "Renaico", "Saavedra", "Teodoro Schmidt",
                       "Tolten", "Traiguen"])

        # Estructura de datos que asocia cada conjunto de ciudades con su zona sísmica
        zone_mapping = [(citiesZone1, 1), (citiesZone2, 2), (citiesZone3, 3)]

        for cities, zone in zone_mapping:
            if loc in cities:
                return zone

        raise NCh433Error(f"UE: location '{loc}' can not be found in any seismic zone")

    @staticmethod
    def computeSoilParameters_c4_2(soil_category):
        soil_parameters = {
            'A':{'S':0.9,  'To': 0.15, 'Tp': 0.2, 'n': 1.,  'p': 2.},
            'B':{'S':1.,   'To':0.3,   'Tp':0.35, 'n':1.33, 'p':1.5},
            'C':{'S':1.05, 'To':0.4,   'Tp':0.45, 'n':1.4,  'p':1.6},
            'D':{'S':1.2,  'To':0.75,  'Tp':0.85, 'n':1.8,  'p':1.},
            'E':{'S':1.3,  'To':1.2,   'Tp':1.35, 'n':1.8,  'p':1.}}
        if soil_category not in soil_parameters: raise NCh433Error(f'NCh433 soil category: category {soil_category} is not valid. Must be either A, B, C, D or E.')
        return soil_parameters[soil_category]
    
    @staticmethod
    def computeImportanceFactor_c4_3(occupation_category):
        # Mapeo de categoría de ocupación a factor de importancia
        importance_factors = {1: 0.6, 2: 1.0, 3: 1.2, 4: 1.2}

        # Retorna el factor de importancia basado en la categoría de ocupación
        if occupation_category not in importance_factors: raise NCh433Error(f"NCh433 importance factor: category '{occupation_category}' is not valid. Must be either 1, 2, 3 or 4")
        return importance_factors[occupation_category]
    
    @staticmethod
    def compute_Tast(direction):
        if direction not in ['x', 'y', 'z']: raise NCh433Error(f"NCh433 Tast: direction '{direction}' is not valid. Must be either 'x', 'y' or 'z'")
        Tast_mapping     ={
            'x': 1.44514,
            'y': 2.16259,
            'z': 0.292927}
        return Tast_mapping[direction]
    
    def computePGA_c6_2_3_2(self, Z):
        # Mapeo de la zona sísmica al factor Ao multiplicado por g
        seismic_zones = {1: 0.2 * self.g, 2: 0.3 * self.g, 3: 0.4 * self.g}

        # Retorna el valor de Ao basado en la zona sísmica
        if Z not in seismic_zones: raise NCh433Error(f"NCh433 PGA: zone '{Z}' is not valid. Must be either 1, 2 or 3")
        return seismic_zones[Z]
    

    # ===================================================
    # BASE SHEAR
    # ===================================================
    def computeCMax_c6_2_3_1_2(self):
        # parameters
        R = self.R
        g = self.g
        soil_params = self.computeSoilParameters_c4_2(self.soil_category)
        S = soil_params["S"]
        Ao = self.computePGA_c6_2_3_2(self.zone)

        # compute the Cmax
        Cmax = None
        tol = 1e-3  # Tolerancia para la comparación
        if   math.isclose(R, 2.0, abs_tol=tol):  Cmax = 0.9  * S * Ao / g
        elif math.isclose(R, 3.0, abs_tol=tol):  Cmax = 0.6  * S * Ao / g
        elif math.isclose(R, 4.0, abs_tol=tol):  Cmax = 0.55 * S * Ao / g
        elif math.isclose(R, 5.5, abs_tol=tol):  Cmax = 0.4  * S * Ao / g
        elif math.isclose(R, 6.0, abs_tol=tol):  Cmax = 0.35 * S * Ao / g
        elif math.isclose(R, 7.0, abs_tol=tol):  Cmax = 0.35 * S * Ao / g
        else:
            raise NCh433Error("UE: NCh433 compute CMax: R factor must be either 2, 3, 4, 5.5, 6 or 7")

        return Cmax

    def computeSeismicCoefficient_c6_2_3_1(self, direction):
        # compute variables
        Tast = self.compute_Tast(direction)
        R = self.R
        g = self.g
        Ao = self.computePGA_c6_2_3_2(self.zone)
        soil_params = self.computeSoilParameters_c4_2(self.soil_category)
        Tp = soil_params['Tp']
        n  = soil_params['n']

        # [6.2.3.1] compute the seismic coefficient.
        C = 2.75*Ao/(g*R) * (Tp/Tast)**n

        # [6.2.3.1.1] limit by minimum
        Cmin = Ao/6./g
        C = max(C, Cmin)

        # [6.2.3.1.2] limit by maximum
        Cmax = self.computeCMax_c6_2_3_1_2()
        C = min(C, Cmax)

        return C

    def computeStaticBaseShear_c6_2_3(self, direction, W):
        """

        :param Tast: fundamental period in the direction of analysis
        :param R: reduction factor
        :param W: seismic weight, associated to the seismic mass sources.
        :return: static base shear.
        """
        R = self.R
        C = self.computeSeismicCoefficient_c6_2_3_1(direction)
        I = self.importance
        Q = C * I * W
        return Q

    def computeMinBaseShear_c6_3_7_1(self, W):
        """
        :param W: seismic weight
        :return: minimum base shear
        """
        g = self.g
        Importance = self.importance
        Ao = self.computePGA_c6_2_3_2(self.zone)
        Qmin = Importance*Ao*W/(6.*g)
        return Qmin

    def computeMaxBaseShear_c6_3_7_2(self, W):
        Importance = self.importance
        Cmax = self.computeCMax_c6_2_3_1_2()
        Qmax = Importance*Cmax*W
        return Qmax








