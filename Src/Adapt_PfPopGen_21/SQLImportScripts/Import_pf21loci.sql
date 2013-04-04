USE pf21c;

DROP TABLE IF EXISTS pf21loci;

CREATE TABLE `pf21loci` (
  `LocusID` varchar(20) DEFAULT NULL,
  `ordr` int(11) DEFAULT NULL,
  `GenomicRegion` varchar(20) DEFAULT NULL,
  `LocusType` varchar(20) DEFAULT NULL,
  `GeneName` varchar(20) DEFAULT NULL,
  `Name` varchar(20) DEFAULT NULL,
  `Comments` varchar(1000) DEFAULT NULL
);


LOAD DATA INFILE 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/pf21loci.txt'
    INTO TABLE pf21loci
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 LINES
    ;
