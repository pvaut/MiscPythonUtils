USE pf21c;
DROP TABLE IF EXISTS pfsnprel21;
CREATE TABLE pfsnprel21 (

num VARCHAR(10),
chrom INT,
pos INT,
snpid VARCHAR(20),
ref VARCHAR(2),
nonrref VARCHAR(2),
outgroup VARCHAR(2),
ancestral VARCHAR(2),
derived VARCHAR(2),
pvtAllele VARCHAR(2),
pvtPop VARCHAR(5),
GeneId VARCHAR(20),
GeneDescription VARCHAR(500),
Strand VARCHAR(2),
CodonNum int,
Codon VARCHAR(3),
NtPos int,
RefAmino VARCHAR(2),
Mutation VARCHAR(2),
MutCodon VARCHAR(3),
MutAmino VARCHAR(2),
MutType VARCHAR(2),
MutName VARCHAR(10),

NRAF_WAF DOUBLE,
NRAF_EAF DOUBLE,
NRAF_SAS DOUBLE,
NRAF_WSEA DOUBLE,
NRAF_ESEA DOUBLE,
NRAF_PNG DOUBLE,
NRAF_SAM DOUBLE,

MAF_WAF DOUBLE,
MAF_EAF DOUBLE,
MAF_SAS DOUBLE,
MAF_WSEA DOUBLE,
MAF_ESEA DOUBLE,
MAF_PNG DOUBLE,
MAF_SAM DOUBLE,

DAF_WAF DOUBLE,
DAF_EAF DOUBLE,
DAF_SAS DOUBLE,
DAF_WSEA DOUBLE,
DAF_ESEA DOUBLE,
DAF_PNG DOUBLE,
DAF_SAM DOUBLE
);
LOAD DATA INFILE 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/pfsnprel21.txt'
    INTO TABLE pfsnprel21
    FIELDS TERMINATED BY '\t'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 LINES
    ;
CREATE INDEX snp_chrom on pfsnprel21 (chrom);
CREATE INDEX snp_pos on pfsnprel21 (pos);
CREATE INDEX snp_snpid on pfsnprel21 (snpid);
CREATE INDEX snp_geneid on pfsnprel21 (GeneId);
SET SQL_SAFE_UPDATES=0;

#alter table pfsnprel21 drop column aliases;
ALTER TABLE pfsnprel21 ADD aliases VARCHAR(200);

UPDATE pfsnprel21,pfannotrel21
    SET pfsnprel21.aliases = pfannotrel21.fnames
    WHERE pfsnprel21.GeneId = pfannotrel21.fid;