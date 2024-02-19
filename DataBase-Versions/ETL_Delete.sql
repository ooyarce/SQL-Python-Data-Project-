# Use this to delete specified rows in tables
DELETE FROM simulation WHERE IDSimulation >=0;
DELETE FROM simulation_sm_input WHERE IDSM_Input >=0;
DELETE FROM model_specs_box WHERE IDBox_specs >= 0;
DELETE FROM model_specs_global WHERE IDSpecs_global >= 0;
DELETE FROM simulation_model  WHERE IDModel >=0;
DELETE FROM sm_input_spectrum WHERE IDSpectrum >=0;
DELETE FROM sm_input_pga WHERE IDPGA >=0;
DELETE FROM model_benchmark WHERE IDBenchmark >=0;
DELETE FROM model_specs_structure  WHERE IDSpecsStructure >=0;
DELETE FROM model_structure_perfomance  WHERE IDStructuralPerfomance >=0;
DELETE FROM structure_max_base_shear  WHERE IDMaxBaseShear >=0;
DELETE FROM structure_abs_acceleration WHERE IDAbsAcceleration >=0;
DELETE FROM structure_relative_displacements WHERE IDRelativeDisplacements >=0;

