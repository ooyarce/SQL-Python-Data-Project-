SELECT mb.JobName,
  CASE SUBSTRING(mb.JobName, 14, 1) #THE NUMBER 14 REFERS TO THE CHARACTER INDEX OF THE STATION NUMBER,CHANGE IN BASE OF JobName
    WHEN '8' THEN 'Far field Center'
    WHEN '7' THEN 'Far field North'
    WHEN '9' THEN 'Far field South'
    ELSE si.Location
  END AS DetailedLocation,
  sms.MaxX, sms.MaxY, sms.MaxZ
FROM simulation_sm_input AS si
JOIN simulation AS s ON s.idSM_Input = si.IDSM_Input
JOIN simulation_model AS sm ON s.idModel = sm.IDModel
JOIN model_benchmark AS mb ON sm.idBenchmark = mb.IDBenchmark
JOIN model_specs_structure AS mss ON sm.idSpecsStructure = mss.IDSpecsStructure
JOIN model_structure_perfomance AS msp ON sm.IDStructuralPerfomance = msp.IDStructuralPerfomance
JOIN structure_max_base_shear AS sms ON msp.idMaxBaseShear = sms.IDMaxBaseShear
WHERE mss.Nhistories = 55 AND mss.Nsubs = 7 AND si.Location = 'Far field'
ORDER BY mb.JobName ASC;
