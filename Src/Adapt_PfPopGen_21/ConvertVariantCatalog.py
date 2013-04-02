from TableUtils import VTTable
import sys

basedir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04'

rowCount=-1

freqList=['nraf','maf','daf']

#freqList=['daf']

#-------------------------------------------------------------------------
tablePopInfo=VTTable.VTTable()
tablePopInfo.allColumnsText=True
tablePopInfo.LoadFile(basedir+"/Definition-Populations.tab")
#tablePopInfo.PrintRows(0,999)
popList=tablePopInfo.GetColStateList('ID')
print('Populations: '+str(popList))


#-------------------------------------------------------------------------
tableSnpInfo=VTTable.VTTable()
tableSnpInfo.allColumnsText=True
tableSnpInfo.LoadFile(basedir+"/SnpInfo.tab",rowCount)
#tableSnpInfo.RemoveEmptyRows()
tableSnpInfo.ColumnRemoveQuotes('GeneDescription')
tableSnpInfo.MapCol('Chr',lambda st: st[3:])

for freq in freqList:
    tableFreqInfo=VTTable.VTTable()
    tableFreqInfo.allColumnsText=True
    tableFreqInfo.LoadFile(basedir+"/Allelefreq-{0}.tab".format(freq),rowCount)
    for pop in popList:
        tableFreqInfo.MapCol(pop,lambda st: float(st) if st!='-' else None)
        tableFreqInfo.RenameCol(pop,'{0}_{1}'.format(freq.upper(),pop))
    tableFreqInfo.DropCol('Num')
    tableFreqInfo.DropCol('Chr')
    tableFreqInfo.DropCol('Pos')
    if tableFreqInfo.IsColumnPresent('Overall'):
        tableFreqInfo.DropCol('Overall')
    tableFreqInfo.PrintRows(0,20)
    colNrSnpName1=tableSnpInfo.GetColNr('SnpName')
    colNrSnpName2=tableFreqInfo.GetColNr('SnpName')
    newTable=VTTable.VTTable()
    newTable.MergeTablesByKeyFrom(tableSnpInfo, tableFreqInfo, 'SnpName', True, True)
    tableSnpInfo=newTable
    
tableSnpInfo.PrintRows(0,20)
    
tableSnpInfo.SaveFile(basedir+'/Output/pfsnprel21.txt',True,'\N')

for col in tableSnpInfo.GetColList():
    ColInfo=tableSnpInfo.GetColInfo(col)
    print(ColInfo.Name)

print('Finished')