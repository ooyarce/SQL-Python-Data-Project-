# ==================================================================================
# IMPORT LIBRARIES
# ==================================================================================
from pyseestko.errors import DataBaseError
import mysql.connector

# ==================================================================================
# SECONDARY CLASSES
# ==================================================================================
class DataBaseManager:
    """
    This class is used to manage the connection to the database.
    """
    def __init__(self, user: str, password: str, host: str, database: str, verbose:bool = True):
        self.cnx = mysql.connector.connect(user=user,
                                           password=password,
                                           host=host,
                                           database=database)
        self.cursor = self.cnx.cursor()

    def insert_data(self, query: str, values: tuple):
        self.cursor.execute(query, values)
        self.cnx.commit()

    def close_connection(self):
        self.cursor.close()
        self.cnx.close()

    def get_nodes_and_elements(self, glob_nnodes:int, glob_nelements:int, stories:int, subs:int, _sim_type:int):
        """
        This function is used to get the nodes and elements of the model.

        Parameters
        ----------
        glob_nnodes : int
            Number of nodes of the model.
        glob_nelements : int
            Number of elements of the model.
        stories : int
            Number of stories of the model.
        subs : int
            Number of subterrains of the model.
        _sim_type : int
            Simulation type of the model.

        Returns
        -------
        str_nnodes : int
            Number of nodes of the structure.
        str_nelements : int
            Number of elements of the structure.
        soil_nnodes : int
            Number of nodes of the soil.
        soil_nelements : int
            Number of elements of the soil.
        """
        if _sim_type == 1:
            str_nnodes     = glob_nnodes
            str_nelements  = glob_nelements

        else:
            try:
                search_query =  f"""SELECT mss.Nnodes, mss.Nelements
                                FROM simulation sim
                                JOIN simulation_model sm ON sim.idModel = sm.IDModel
                                JOIN model_specs_structure mss ON sm.idSpecsStructure = mss.IDSpecsStructure
                                WHERE sim.idType = 1 AND mss.Nstories = {stories} AND mss.Nsubs= {subs};
                                """
                self.cursor.execute(search_query)
                existing_entry = self.cursor.fetchall()
                str_nnodes     = existing_entry[0][0] # type: ignore
                str_nelements  = existing_entry[0][1] # type: ignore
            except IndexError as e:
                raise DataBaseError('No entries found in model_specs_structure.\n Please check if FixBaseModels are uploaded or check the query.') from e

        soil_nnodes    = glob_nnodes    - str_nnodes    # type: ignore
        soil_nelements = glob_nelements - str_nelements # type: ignore
        return str_nnodes, str_nelements, soil_nnodes, soil_nelements

    def check_if_sm_input(self, unique_values: tuple):
        cursor = self.cursor
        search_query = """
        SELECT idSM_Input FROM simulation_sm_input
        WHERE Magnitude = %s AND Rupture_type = %s AND Location = %s AND RealizationID = %s
        """
        cursor.execute(search_query, unique_values)
        existing_entry = cursor.fetchone() # Returns None if no entry is found and the ID if it is found
        return existing_entry

    def check_if_specs_structure(self, unique_values: tuple):
        cursor = self.cursor
        search_query = """
        SELECT IDSpecsStructure FROM model_specs_structure
        WHERE idLinearity = %s AND Nnodes = %s AND Nelements = %s AND Nstories= %s AND Nsubs = %s
        AND InterstoryHeight = %s
        AND Comments = %s"""
        cursor.execute(search_query, unique_values)
        existing_entry = cursor.fetchone()
        return existing_entry








