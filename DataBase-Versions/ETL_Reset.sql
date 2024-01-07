# WARNING! RUN THE FOLLOWING COMMAND JUST TO RESET ALL THE DATABASE

/*
============================================================================|
This tables should not be modified since the data is fixed and not may vary |
============================================================================|
SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE simulation_type;
TRUNCATE TABLE model_linearity;
TRUNCATE TABLE sm_input_spectrum;
TRUNCATE TABLE sm_input_pga;
TRUNCATE TABLE simulation_sm_input;
SET FOREIGN_KEY_CHECKS=1;
*/

/*
============================================================================|
This tables should be modified to reset all the simulation results 			|
============================================================================|
*/
SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE simulation;
TRUNCATE TABLE simulation_model ;
TRUNCATE TABLE model_benchmark;
TRUNCATE TABLE model_specs_structure ;
TRUNCATE TABLE model_structure_perfomance ;
TRUNCATE TABLE structure_max_drift_per_floor;
TRUNCATE TABLE structure_abs_acceleration;
TRUNCATE TABLE structure_relative_displacements;
TRUNCATE TABLE structure_max_base_shear ;
TRUNCATE TABLE structure_base_shear;
SET FOREIGN_KEY_CHECKS=1;