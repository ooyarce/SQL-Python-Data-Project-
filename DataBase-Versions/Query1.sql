SELECT * FROM simulation WHERE IDSimulation >= 0;
SELECT * FROM simulation_model  WHERE IDModel >= 0;
SELECT * FROM model_benchmark WHERE IDBenchmark >= 0;
SELECT * FROM model_specs_structure  WHERE IDSpecsStructure >= 0;
SELECT * FROM model_structure_perfomance  WHERE IDStructuralPerfomance >= 0;
SELECT * FROM structure_max_base_shear  WHERE IDMaxBaseShear >=0;
SELECT * FROM structure_abs_acceleration WHERE IDAbsAcceleration >=0;
SELECT * FROM simulation_type;
SELECT * FROM model_linearity;
SELECT * FROM structure_max_drift_per_floor  WHERE IDMaxDriftPerFloor >= 0;
SELECT * FROM simulation_sm_input  WHERE IDSM_Input >= 0;
SELECT * FROM sm_input_pga WHERE IDPGA >= 0;
SELECT * FROM sm_input_spectrum WHERE IDSpectrum >= 0;
SELECT * FROM simulation_type WHERE IDType >= 0;
# To setup all index autoincrement from 0:
#ALTER TABLE tu_tabla AUTO_INCREMENT = 1;

DELETE FROM simulation WHERE IDSimulation >=0;
DELETE FROM simulation_sm_input WHERE IDSM_Input >=0;
DELETE FROM simulation_model  WHERE IDModel >=0;
DELETE FROM sm_input_spectrum WHERE IDSpectrum >=0;
DELETE FROM sm_input_pga WHERE IDPGA >=0;
DELETE FROM model_benchmark WHERE IDBenchmark >=0;
DELETE FROM model_specs_structure  WHERE IDSpecsStructure >=0;
DELETE FROM model_structure_perfomance  WHERE IDStructuralPerfomance >=0;
DELETE FROM structure_max_base_shear  WHERE IDMaxBaseShear >=0;
DELETE FROM structure_abs_acceleration WHERE IDAbsAcceleration >=0;
DELETE FROM structure_relative_displacements WHERE IDRelativeDisplacements >=0