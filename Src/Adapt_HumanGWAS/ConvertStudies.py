from TableUtils import VTTable
import sys
import hashlib






basedir = 'C:/Data/Genomes/HumanGWAS/MetaData'


# Build index of all available studies
tableStudies=VTTable.VTTable()
tableStudies.allColumnsText=True
#tableStudies.LoadFile(basedir+"/PartnerStudies.txt")
tableStudies.LoadXls(basedir+"/Studies.xlsx","Sheet1")

RowNr=0;
while RowNr<tableStudies.GetRowCount():
    if tableStudies.GetValue(RowNr,tableStudies.GetColNr('Use'))=='N':
        tableStudies.RemoveRow(RowNr)
    else:
        RowNr+=1
        
tableStudies.DropCol('title')  
tableStudies.RenameCol('LocationName', 'title')
        
tableStudies.DropCol('country')  
#tableStudies.DropCol('LocationName')  
tableStudies.DropCol('Use')
tableStudies.ArrangeColumns(['study','title'])  

tableStudies.PrintRows(0,9999)

tableStudies.SaveSQLDump(basedir+'/Output/studies.sql', 'study')