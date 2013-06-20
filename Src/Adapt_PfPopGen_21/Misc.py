from TableUtils import VTTable
#import MySQLdb
import sys
import math
#import DataProviders
#import sets


if False:
    tb=VTTable.VTTable()
    tb.allColumnsText=True
    tb.LoadFile('/home/pvaut/Documents/Genome/PfPopgen21/AlleleFreq-nraf.tab')

    tb.DropCol('Num')
    tb.ConvertColToValue('Pos')
    freqs=['Overall','BD','BF','CO','GH','GM','GN','KE','KH','LA','ML','MM','MW','PE','PG','TH','TZ','VN']
    for freq in freqs:
        tb.ConvertColToValue(freq)

    tb.RenameCol('Chr','chrom')
    tb.RenameCol('Pos','pos')
    tb.RenameCol('SnpName','snpid')
    tb.PrintRows(0,9)
    tb.SaveSQLCreation('/home/pvaut/Documents/Genome/PfPopgen21/AlleleFreq-nraf_creation.sql','country_nraf')
    tb.SaveSQLDump('/home/pvaut/Documents/Genome/PfPopgen21/AlleleFreq-nraf.sql','country_nraf')

if True:
    tb=VTTable.VTTable()
    tb.allColumnsText=True
    tb.LoadFile('/home/pvaut/Documents/Genome/PfPopgen21/snpgroups.txt')
    tb.PrintRows(0,999)
    tb.SaveSQLCreation('/home/pvaut/Documents/Genome/PfPopgen21/snpgroups_creation.sql','snpgroups')
    tb.SaveSQLDump('/home/pvaut/Documents/Genome/PfPopgen21/snpgroups.sql','snpgroups')

    tb=VTTable.VTTable()
    tb.allColumnsText=True
    tb.LoadXls('/home/pvaut/Documents/Genome/PfPopgen21/allSNPs.xlsx','Sheet1')
    tb.MergeColsToString("snpid","MAL{0}:{1}","chrom","pos")
    tb.DropCol('sequence_code')
    tb.DropCol('chr_valid')
    tb.DropCol('coord_valid')
    tb.DropCol('multiplex_code')
    tb.DropCol('gene_symbol')
    tb.DropCol('Group')
    tb.DropCol('chrom')
    tb.DropCol('pos')
    tb.AddIndexCol('idx')
    tb.PrintRows(0,999)
    tb.SaveSQLDump('/home/pvaut/Documents/Genome/PfPopgen21/snpgroupmembers.sql','snpgroupmembers')


if False:
    tb=VTTable.VTTable()
    tb.allColumnsText=True
    tb.LoadFile('/home/pvaut/Documents/Genome/PfPopgen21/snpgroups.txt')
    tb.PrintRows(0,999)
    tb.SaveSQLCreation('/home/pvaut/Documents/Genome/PfPopgen21/snpgroups_creation.sql','snpgroups')
    tb.SaveSQLDump('/home/pvaut/Documents/Genome/PfPopgen21/snpgroups.sql','snpgroups')
    tb=VTTable.VTTable()
    tb.allColumnsText=True
    tb.LoadFile('/home/pvaut/Documents/Genome/PfPopgen21/snpgroupmembers.txt')
    tb.AddIndexCol('idx')
    tb.PrintRows(0,999)
    tb.SaveSQLCreation('/home/pvaut/Documents/Genome/PfPopgen21/snpgroupmembers_creation.sql','snpgroupmembers')
    tb.SaveSQLDump('/home/pvaut/Documents/Genome/PfPopgen21/snpgroupmembers.sql','snpgroupmembers')



sys.exit()






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