from TableUtils import VTTable
import sys

basedir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04'


#-------------------------------------------------------------------------
tableSamples=VTTable.VTTable()
tableSamples.allColumnsText=True
tableSamples.LoadFile(basedir+"/samples.txt")
tableSamples.DropCol('Notes')
tableSamples.DropCol('SiteInfoSource')
tableSamples.DropCol('LabSample')
tableSamples.DropCol('LowTypability')
tableSamples.DropCol('PcaOutlier')
tableSamples.DropCol('IsDuplicate')
tableSamples.DropCol('ManualExlusion')
tableSamples.DropCol('Typability')
tableSamples.DropCol('UsedInSnpDiscovery')
tableSamples.DropCol('Location')
tableSamples.DropCol('SubCont')
tableSamples.DropCol('KhCluster')
tableSamples.DropCol('Region')
tableSamples.DropCol('Fws')
tableSamples.DropCol('Year')



#tableSamples.RemoveEmptyRows()
#tableSamples.ColumnRemoveQuotes('Comments')

#Remove excluded samples
ColNrExclusion=tableSamples.GetColNr('Exclude')
RowNr=0
while RowNr<tableSamples.GetRowCount():
    if tableSamples.GetValue(RowNr,ColNrExclusion)!='FALSE':
        tableSamples.RemoveRow(RowNr)
    else:
        RowNr+=1
        
tableSamples.MergeColsToString('SampleContext','{0}_{1}','Study','SiteCode')

tableSamples.PrintRows(0,10)

#-------------------------------------------------------------------------
tableSampleGroups=VTTable.VTTable()
tableSampleGroups.allColumnsText=True
tableSampleGroups.LoadFile(basedir+"/SampleGroups.tab")
tableSampleGroups.DropCol('Group')
tableSampleGroups.PrintRows(0,10)

tableSampleGlobal=VTTable.VTTable()
tableSampleGlobal.MergeTablesByKeyFrom(tableSamples, tableSampleGroups, 'Sample', True, True)


tableContextClassif=VTTable.VTTable()
tableContextClassif.AddColumn(VTTable.VTColumn('ContextClassif','Text'))
tableContextClassif.AddColumn(VTTable.VTColumn('count','Value'))

Classifications=[{'ID':'region', 'Column':'Country'}, {'ID':'subcont', 'Column':'Pop'}]

for Classif in Classifications:
    ColContextClassif=Classif['ID']+'_SampleContext'
    tableSampleGlobal.MergeColsToString(ColContextClassif,'{0}~{1}',Classif['Column'],'SampleContext')
    StateList=tableSampleGlobal.GetColStateCountList(ColContextClassif)
    #print(str(StateList))
    for state in StateList:
        tableContextClassif.AddRowEmpty()
        tableContextClassif.SetValue(tableContextClassif.GetRowCount()-1, 0, state)
        tableContextClassif.SetValue(tableContextClassif.GetRowCount()-1, 1, StateList[state])
    
tableSampleGlobal.PrintRows(0, 10)

tableContextClassif.CalcCol('sample_classification',lambda st:st.split('~')[0],'ContextClassif')
tableContextClassif.CalcCol('sample_context',lambda st:st.split('~')[1],'ContextClassif')
tableContextClassif.DropCol('ContextClassif')
tableContextClassif.ArrangeColumns(['sample_classification','sample_context','count'])

tableContextClassif.PrintRows(0, 100000)

tableContextClassif.SaveFile(basedir+'/Output/sample_classification_context_count.txt', True, '')
