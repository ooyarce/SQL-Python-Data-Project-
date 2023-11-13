SELECT * FROM simulation WHERE IDSimulation >= 0;
SELECT * FROM simulation_model  WHERE IDModel >= 0;
SELECT * FROM model_benchmark WHERE IDBenchmark >= 0;
SELECT * FROM model_specs_structure  WHERE IDSpecsStructure >= 0;
SELECT * FROM model_structure_perfomance  WHERE IDStructuralPerfomance >= 0;
SELECT * FROM structure_max_base_shear  WHERE IDMaxBaseShear >=0;
SELECT * FROM structure_abs_acceleration WHERE IDAbsAcceleration >=0;

SELECT * FROM structure_max_drift_per_floor  WHERE IDMaxDriftPerFloor >= 0;
SELECT * FROM simulation_sm_input  WHERE IDSM_Input >= 0;

# To setup all index autoincrement from 0:
#ALTER TABLE tu_tabla AUTO_INCREMENT = 1;

TRUNCATE TABLE simulation;
TRUNCATE TABLE simulation_model ;
TRUNCATE TABLE model_benchmark;
TRUNCATE TABLE model_specs_structure ;
TRUNCATE TABLE model_structure_perfomance ;
TRUNCATE TABLE structure_max_base_shear ;
TRUNCATE TABLE structure_abs_acceleration;