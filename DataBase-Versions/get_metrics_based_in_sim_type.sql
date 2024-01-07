# THE FOLLOWING SCRIPT WILL FILTER THE METRICS BASED IN THE SIM TYPE
# THAT MEANS THAT WE SHOULD READ THE FOLLOWING SCRIPT AS:
# -> I WANT ALL THE "DRM-LINEAR" RESULTS"

# SO WE WILL HAVE THE MODEL PERFOMANCE METRICS ASSOCIATED TO THAT GROUP.
SELECT msp.*
FROM simulation sim
JOIN simulation_model sm ON sim.idModel = sm.IDModel
JOIN model_specs_structure mss ON sm.idSpecsStructure = mss.IDSpecsStructure
JOIN model_structure_perfomance msp ON sm.idStructuralPerfomance = msp.IDStructuralPerfomance
WHERE sim.idType = 1 AND mss.idLinearity = 1;


 SELECT * FROM simulation_sm_input
WHERE Magnitude = '6.5 Mw' AND Rupture_type = 'Bilateral' AND Location = 'UAndes Campus' AND RealizationID = 1;
 
 
ALTER TABLE simulation_sm_input
ADD CONSTRAINT unique_simulation_input UNIQUE(Magnitude, Rupture_Type, Location, RealizationID);
