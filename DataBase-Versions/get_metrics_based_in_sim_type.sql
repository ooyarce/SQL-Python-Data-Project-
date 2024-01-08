# THE FOLLOWING SCRIPT WILL FILTER THE METRICS BASED IN THE SIM TYPE
# THAT MEANS THAT WE SHOULD READ THE FOLLOWING SCRIPT AS:
# -> I WANT ALL THE "DRM-LINEAR" RESULTS"

# SO WE WILL HAVE THE MODEL PERFOMANCE METRICS ASSOCIATED TO THAT GROUP.
# Filter metrics by type and linearity but not with building type
# In that case you will need to add Nstories and Nsubs from model_specs_structures
# as filtering parameters.
SELECT msp.*
FROM simulation sim
JOIN simulation_model sm ON sim.idModel = sm.IDModel
JOIN model_specs_structure mss ON sm.idSpecsStructure = mss.IDSpecsStructure
JOIN model_structure_perfomance msp ON sm.idStructuralPerfomance = msp.IDStructuralPerfomance
WHERE sim.idType = 1 AND mss.idLinearity = 1;


# Filter building by simulation type, stories and subs
SELECT mss.*
FROM simulation sim
JOIN simulation_model sm ON sim.idModel = sm.IDModel
JOIN model_specs_structure mss ON sm.idSpecsStructure = mss.IDSpecsStructure
WHERE sim.idType = 1 AND mss.Nstories = 20 AND mss.Nsubs= 2;


# Filter input
 SELECT * FROM simulation_sm_input
WHERE Magnitude = '6.5 Mw' AND Rupture_type = 'Bilateral' AND Location = 'UAndes Campus' AND RealizationID = 1;
 
SELECT * FROM model_specs_structure
WHERE idLinearity = 1 AND Nnodes = 26057 AND Nelements = 35972 AND Nstories= 20 AND Nsubs = 2
AND InterstoryHeight = '[3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5]'
AND Comments = 'Linear-elastic elements: FixBase-6.5-bl-1-s0'
/*
This was to make the tables with no repeated values

ALTER TABLE simulation_sm_input
ADD CONSTRAINT unique_simulation_input UNIQUE(Magnitude, Rupture_Type, Location, RealizationID);

ALTER TABLE model_specs_structure
ADD CONSTRAINT unique_structure_specs UNIQUE(idLinearity, Nnodes, Nelements, Nstories, Nsubs, InterstoryHeight, Comments);
*/