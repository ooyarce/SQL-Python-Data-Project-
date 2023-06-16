SELECT mb.JobName, si.Location, sms.IDMaxBaseShear
FROM simulation AS s
JOIN simulation_sm_input AS si ON s.idSM_Input = si.IDSM_Input
JOIN simulation_model AS sm ON s.idModel = sm.IDModel
JOIN model_benchmark AS mb ON sm.idBenchmark = mb.IDBenchmark
JOIN model_specs_structure AS mss ON sm.idSpecsStructure = mss.IDSpecsStructure
JOIN model_structure_perfomance AS msp on sm.IDStructuralPerfomance = msp.IDStructuralPerfomance
JOIN structure_max_base_shear AS sms ON msp.idMaxBaseShear = sms.IDMaxBaseShear
WHERE mss.Nhistories = 55 AND mss.Nsubs = 7 AND Location = 'Mid field';

