USE pf21c;

DROP TABLE IF EXISTS pf21geneinfo;

CREATE TABLE pf21geneinfo (
  GeneName varchar(20),
  ordr int,
  Chromosome varchar(10),
  Description varchar(200),
  Comments varchar(1000)
);

LOAD DATA INFILE 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/pf21geneinfo.txt'
    INTO TABLE pf21geneinfo
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 LINES
    ;
