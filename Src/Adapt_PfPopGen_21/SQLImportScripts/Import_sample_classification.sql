USE pf21c;

DROP TABLE IF EXISTS sample_classification;


CREATE TABLE `sample_classification` (
  `ordr` int DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `sample_classification` varchar(50) NOT NULL,
  `sample_classification_type` varchar(50) DEFAULT NULL,
  `longit` double DEFAULT NULL,
  `lattit` double DEFAULT NULL,
  `geo_json` text,
  PRIMARY KEY (`sample_classification`)
);


LOAD DATA INFILE 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/sample_classification.txt'
    INTO TABLE sample_classification
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 LINES
    ;
