# Use this to access to the database info as a preset. Ideally you use it later in python.
SELECT * FROM simulation_type;
SELECT * FROM model_linearity;

# Simulation info tables
SELECT * FROM simulation 		WHERE IDSimulation >= 0;
SELECT * FROM simulation_model  WHERE IDModel >= 0;

# Input info tables
SELECT * FROM simulation_sm_input  WHERE IDSM_Input >= 0;
SELECT * FROM sm_input_pga 		   WHERE IDPGA >= 0;
SELECT * FROM sm_input_spectrum    WHERE IDSpectrum >= 0;

# Model info tables
SELECT * FROM model_benchmark 		      WHERE IDBenchmark >= 0;
SELECT * FROM model_specs_structure       WHERE IDSpecsStructure >= 0;
SELECT * FROM model_specs_box  		 	  WHERE IDBox_specs >= 0;
SELECT * FROM model_specs_global  	 	  WHERE IDSpecs_global >= 0;
SELECT * FROM model_structure_perfomance  WHERE IDStructuralPerfomance >= 0;

# Perfomance metrics info tables
SELECT * FROM structure_max_drift_per_floor    WHERE IDMaxDriftPerFloor >= 0;
SELECT * FROM structure_abs_acceleration 	   WHERE IDAbsAcceleration >=0;
SELECT * FROM structure_relative_displacements WHERE IDRelativeDisplacements >=0;
SELECT * FROM structure_max_base_shear  	   WHERE IDMaxBaseShear >=0;
SELECT * FROM structure_base_shear  		   WHERE IDBaseShear >=0;



