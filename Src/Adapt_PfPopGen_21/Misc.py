from TableUtils import VTTable
import MySQLdb
import sys
import math
import DataProviders
import sets


meta = {
      'DBSRV':'localhost',
      'DBUSER':'root',
      'DBPASS':'1234',
      'DB':'world',
      'SOURCEDIR':'C:/Data/Genomes/PlasmodiumFalciparum/Release_21'
      }


sitetable=VTTable.VTTable()
sitetable.allColumnsText=True
sitetable.LoadFile(meta['SOURCEDIR']+'/OriginalData/SitesInfo.txt')
sitetable.PrintRows(0,99999)
dct=sitetable.BuildColDict('Name',False)
print(str(dct))


table=VTTable.VTTable()
table.allColumnsText=True
table.LoadFile(meta['SOURCEDIR']+'/OriginalData/metadata-2.0.2_withsites.txt')
for rownr in table.GetRowNrRange():
    sitename=table.GetValue(rownr,'Site')
    if len(sitename)>0:
        if sitename not in dct:
            raise Exception('Invalid site '+sitename)
        siteid=sitetable.GetValue(dct[sitename],'ID')
        table.SetValue(rownr,'Site',siteid)
table.PrintRows(0,99999)
table.SaveFile(meta['SOURCEDIR']+'/OriginalData/metadata-2.0.2_withsites.txt', True, '-')
sys.exit()

siteMap = {}

sampleData = DataProviders.SampleInfoProvider(meta)
for sampleid in sampleData.GetSampleIDs():
    if sampleData.GetSampleInfo(sampleid, 'Exclude') == 'FALSE':
        site = sampleData.GetSampleInfo(sampleid, 'Site')
        country = sampleData.GetSampleInfo(sampleid, 'Country')
        subcont = sampleData.GetSampleInfo(sampleid, 'SubCont')
        study = sampleData.GetSampleInfo(sampleid, 'Study')
        if site not in siteMap:
            siteMap[site] = {'Count':0, 'StudiesMap':{}, 'Country':country, 'SubCont':subcont}
        if country != siteMap[site]['Country']:
            raise Exception('Inconsistent countries') 
        if subcont != siteMap[site]['SubCont']:
            raise Exception('Inconsistent subcont') 
        siteMap[site]['Count'] += 1
        if study not in siteMap[site]['StudiesMap']:
            siteMap[site]['StudiesMap'][study] = 0
        siteMap[site]['StudiesMap'][study]+=1

sites = VTTable.VTTable()
sites.AddColumn(VTTable.VTColumn('Name','Text'))
sites.AddColumn(VTTable.VTColumn('Country','Text'))
sites.AddColumn(VTTable.VTColumn('SubCont','Text'))
sites.AddColumn(VTTable.VTColumn('Count','Value'))
sites.AddColumn(VTTable.VTColumn('Studies','Text'))

for site in siteMap:
    sites.AddRowEmpty()
    sites.SetValue(sites.GetRowCount()-1,0,site)
    sites.SetValue(sites.GetRowCount()-1,1,siteMap[site]['Country'])
    sites.SetValue(sites.GetRowCount()-1,2,siteMap[site]['SubCont'])
    sites.SetValue(sites.GetRowCount()-1,3,siteMap[site]['Count'])
    studycounts=siteMap[site]['StudiesMap']
    studylst=', '.join([study+'('+str(studycounts[study])+')' for study in studycounts ])
    sites.SetValue(sites.GetRowCount()-1,4,studylst)
    #print('')
    #print(site)
    #print(str(siteMap[site]['Count']))
    #print(str(siteMap[site]['StudiesMap']))
    
    
sites.PrintRows(0, 9999)    
sites.SaveFile(meta['SOURCEDIR']+'/SitesInfo.txt',True,'-')