USE pf21c;

DROP TABLE IF EXISTS pf21locusfreqs;


CREATE TABLE `pf21locusfreqs` (
  `AggregTypeID` varchar(20) DEFAULT NULL,
  `AggregShortName` varchar(60) DEFAULT NULL,
  `LocusID` varchar(20) DEFAULT NULL,
  `VariantID` varchar(20) DEFAULT NULL,
  `Count` int(11) DEFAULT NULL
);

LOAD DATA INFILE 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/pf21locusfreqs.txt'
    INTO TABLE pf21locusfreqs
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 LINES
    ;
