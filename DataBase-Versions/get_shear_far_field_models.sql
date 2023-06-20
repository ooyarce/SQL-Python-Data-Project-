SELECT mb.JobName,
  CASE SUBSTRING(mb.JobName, 13, 1) #THE NUMBER 14 REFERS TO THE CHARACTER INDEX OF THE STATION NUMBER,CHANGE IN BASE OF JobName
    WHEN '8' THEN 'Far field Center'
    WHEN '7' THEN 'Far field North'
    WHEN '9' THEN 'Far field South'
    ELSE si.Location
  END AS DetailedLocation,
  CASE SUBSTRING(mb.JobName,4,3)
	WHEN '6.5' THEN 6.5
    WHEN '6.7' THEN 6.7
    WHEN '6.9' THEN 6.9
    WHEN '7.0' THEN 7.0
  END AS Magnitude,
  CASE SUBSTRING(mb.JobName,8,3)
	WHEN 'bl1' THEN 'Bilateral'
    WHEN 'bl2' THEN 'Bilateral'
    WHEN 'bl3' THEN 'Bilateral'
    WHEN 'ns1' THEN 'North-South'
    WHEN 'ns2' THEN 'North-South'
    WHEN 'ns3' THEN 'North-South'
    WHEN 'sn1' THEN 'South-North'
    WHEN 'sn2' THEN 'South-North'
    WHEN 'sn3' THEN 'South-North'
  END AS Rupture,
  sms.MaxX, sms.MaxY, sms.MaxZ
FROM simulation_sm_input AS si
JOIN simulation AS s ON s.idSM_Input = si.IDSM_Input
JOIN simulation_model AS sm ON s.idModel = sm.IDModel
JOIN model_benchmark AS mb ON sm.idBenchmark = mb.IDBenchmark
JOIN model_specs_structure AS mss ON sm.idSpecsStructure = mss.IDSpecsStructure
JOIN model_structure_perfomance AS msp ON sm.IDStructuralPerfomance = msp.IDStructuralPerfomance
JOIN structure_max_base_shear AS sms ON msp.idMaxBaseShear = sms.IDMaxBaseShear
WHERE mss.Nhistories = 20 AND mss.Nsubs = 4 AND si.Location = 'Far field'
ORDER BY mb.JobName ASC;
