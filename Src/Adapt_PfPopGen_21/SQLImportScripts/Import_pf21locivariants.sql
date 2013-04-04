USE pf21c;

DROP TABLE IF EXISTS pf21locivariants;


CREATE TABLE `pf21locivariants` (
  `LocusID` varchar(20) DEFAULT NULL,
  `VariantID` varchar(20) DEFAULT NULL,
  `ordr` int(11) DEFAULT NULL,
  `Mutant` varchar(5) DEFAULT NULL,
  `Name` varchar(20) DEFAULT NULL,
  `Color` varchar(30) DEFAULT NULL,
  `Comments` varchar(2000) DEFAULT NULL
);

LOAD DATA INFILE 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/pf21locivariants.txt'
    INTO TABLE pf21locivariants
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 LINES
    ;
