USE pf21c;

DROP TABLE IF EXISTS sample_classification_context_count;


CREATE TABLE `sample_classification_context_count` (
  `sample_classification` varchar(50),
  `sample_context` varchar(50),
  `count` int
);



LOAD DATA INFILE 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/sample_classification_context_count.txt'
    INTO TABLE sample_classification_context_count
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 LINES
    ;
