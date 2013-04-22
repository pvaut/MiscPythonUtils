from TableUtils import VTTable
import sys

basedir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04'


########################################################################################################"
# Process studies
########################################################################################################"
tableStudies=VTTable.VTTable()
tableStudies.allColumnsText=True
#tableStudies.LoadFile(basedir+"/PartnerStudies.txt")
tableStudies.LoadXls(basedir+"/PartnerStudies.xlsx","PartnerStudies")

UseNewDescription=True

if UseNewDescription:
    tableStudies.DropCol('Previous_Title')
    tableStudies.DropCol('Previous_Description')
else:
    tableStudies.DropCol('Study_title')
    tableStudies.DropCol('Description')
    tableStudies.RenameCol('Previous_Title','Study_title')
    tableStudies.RenameCol('Previous_Description','Description')

tableStudies.ColumnRemoveQuotes('Description')
tableStudies.ColumnRemoveQuotes('Study_title')
tableStudies.DropCol('Triage')
tableStudies.DropCol('MalariaGEN role included')
tableStudies.DropCol('Notes')
    

# Create map from internal study to public study
dct=tableStudies.BuildColDict('Study',True)
MapStudyPrivate2Public = { studyid : tableStudies.GetValue(dct[studyid], tableStudies.GetColNr('PublicStudy')) for studyid in dct }
print('Private to public study map: '+str(MapStudyPrivate2Public))

#remove studies that are private only
RowNr=0
while RowNr<tableStudies.GetRowCount():
    studyid=tableStudies.GetValue(RowNr, tableStudies.GetColNr('Study'))
    if MapStudyPrivate2Public[studyid] != studyid:
        tableStudies.RemoveRow(RowNr)
    else:
        RowNr+=1

tableStudies.MergeColsToString('title', '{0}. {1}','NumID','Study_title')
        
tableStudies.RenameCol('Study','study')
tableStudies.RenameCol('Description','description')
tableStudies.DropCol('NumID')
tableStudies.DropCol('Study_title')
tableStudies.DropCol('PublicStudy')
tableStudies.AddColumn(VTTable.VTColumn('people','Text'))
tableStudies.AddColumn(VTTable.VTColumn('full_study','Value'))
tableStudies.FillColumn('people', '')
tableStudies.FillColumn('full_study', 1)
tableStudies.ArrangeColumns(['study','people','description','full_study','title'])
tableStudies.PrintRows(0,9999)
tableStudies.SaveFile(basedir+'/Output/study.txt', True, '')
tableStudies.SaveSQLDump(basedir+'/Output/study.sql','study')
        

#sys.exit()


########################################################################################################"
# Save locations
########################################################################################################"

#-------------------------------------------------------------------------
tableSites=VTTable.VTTable()
tableSites.allColumnsText=True
tableSites.LoadFile(basedir+"/SitesInfo.txt")
tableSites.DropCol('GeoCode')
tableSites.DropCol('SubCont')
tableSites.ColumnRemoveQuotes('Name')
tableSites.RenameCol('Latitude','lattit')
tableSites.RenameCol('Longitude','longit')
tableSites.RenameCol('Description','description')
tableSites.RenameCol('Country','country')
tableSites.RenameCol('Name','name')
tableSites.RenameCol('ID','location')
tableSites.ConvertColToValue('lattit')
tableSites.ConvertColToValue('longit')
tableSites.ArrangeColumns(['lattit','description','country','location','longit','name'])
tableSites.PrintRows(0,10)
tableSites.SaveFile(basedir+'/Output/location.txt', True, '')
tableSites.SaveSQLDump(basedir+'/Output/location.sql','location')

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



#-------------------------------------------------------------------------
tableSites=VTTable.VTTable()
tableSites.allColumnsText=True
tableSites.LoadFile(basedir+"/SitesInfo.txt")
tableSites.DropCol('Latitude')
tableSites.DropCol('Longitude')
tableSites.DropCol('GeoCode')
tableSites.DropCol('SubCont')
tableSites.DropCol('Description')
tableSites.ColumnRemoveQuotes('Name')
tableSites.PrintRows(0,10)
indexSites= tableSites.BuildColDict('ID', False)


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
        
#Convert private study id's to public study id's
tableSamples.MapCol('Study',lambda studyid : MapStudyPrivate2Public[studyid] )

tableSamples.PrintRows(0,10)
        
        
tableSamples.MergeColsToString('SampleContext','{0}_{1}','Study','SiteCode')

print('Countries: '+str(tableSamples.GetColStateCountList('Country')))

tableSamples.PrintRows(0,10)

print("**** WARNING: TODO: CREATE SAMPLE CONTEXTS DYNAMICALLY FROM STYDIES & SITES RATHER THAN TAKING FROM TABLE")


########################################################################################################"
# Sample contexts
########################################################################################################"

tableSampleContexts=VTTable.VTTable()
tableSampleContexts.AddColumn(VTTable.VTColumn('study','Text'))
tableSampleContexts.AddColumn(VTTable.VTColumn('location','Text'))
tableSampleContexts.AddColumn(VTTable.VTColumn('sample_context','Text'))
tableSampleContexts.AddColumn(VTTable.VTColumn('description','Text'))
tableSampleContexts.AddColumn(VTTable.VTColumn('title','Text'))
tableSampleContexts.AddColumn(VTTable.VTColumn('samplecount','Value'))


sampleContextCounts = tableSamples.GetColStateCountList("SampleContext")
#print("Sample context counts: "+str(sampleContextCounts))
for sampleContextID in sampleContextCounts:
    studyID=sampleContextID.split('_',1)[0]
    siteID=sampleContextID.split('_',1)[1]
    #print(studyID+' '+siteID)
    if siteID not in indexSites:
        raise Exception('Invalid site id '+siteID)
    tableSampleContexts.AddRowEmpty()
    RowNr=tableSampleContexts.GetRowCount()-1
    tableSampleContexts.SetValue(RowNr,tableSampleContexts.GetColNr('study'),studyID)
    tableSampleContexts.SetValue(RowNr,tableSampleContexts.GetColNr('location'),siteID)
    tableSampleContexts.SetValue(RowNr,tableSampleContexts.GetColNr('sample_context'),sampleContextID)
    tableSampleContexts.SetValue(RowNr,tableSampleContexts.GetColNr('description'),'')
    tableSampleContexts.SetValue(RowNr,tableSampleContexts.GetColNr('title'),tableSites.GetValue(indexSites[siteID],tableSites.GetColNr('Name')))
    tableSampleContexts.SetValue(RowNr,tableSampleContexts.GetColNr('samplecount'),sampleContextCounts[sampleContextID])

tableSampleContexts.PrintRows(0,100000)
tableSampleContexts.SaveFile(basedir+'/Output/sample_context.txt', True, '')
tableSampleContexts.SaveSQLDump(basedir+'/Output/sample_context.sql','sample_context')
#sys.exit()


########################################################################################################"
# Sample classifications x sample contexts
########################################################################################################"

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
tableContextClassif.SaveSQLDump(basedir+'/Output/sample_classification_context_count.sql','sample_classification_context_count')
