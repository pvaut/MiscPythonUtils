from TableUtils import VTTable
import sys
import hashlib

def hash(str):
    return hashlib.md5('salt'+str+'pepper'+str).hexdigest()[0:8]

basedir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04'


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

tableSamples.PrintRows(0,9)



fl=open(basedir+'/public_samples.txt','r')
publicSamples=[line.rstrip() for line in fl]
publicSamplesMap={id:True for id in publicSamples}
fl.close()

#Check uniqueness
uniqueMap={}
for smp in publicSamples:
    if hash(smp) in uniqueMap:
        raise Exception('Not unique hash')
    uniqueMap[hash(smp)]=True

print('Public samples: '+str(publicSamples))

#remove non-public samples
RowNr=0
while RowNr<tableSamples.GetRowCount():
    id=tableSamples.GetValue(RowNr,tableSamples.GetColNr('Sample'))
    if id not in publicSamplesMap:
        tableSamples.RemoveRow(RowNr)
    else:
        RowNr += 1

tableSamples.MapCol('Sample', hash)

tableSamples.MergeColsToString('sample_context', '{0}_{1}','Study','SiteCode')

tableSamples.DropCol('Exclude')
tableSamples.DropCol('Study')
tableSamples.DropCol('SiteCode')
tableSamples.DropCol('SiteCodeOriginal')
tableSamples.DropCol('Country')
tableSamples.RenameCol('Sample', 'sample')
tableSamples.AddColumn(VTTable.VTColumn('is_public','Value'))
tableSamples.FillColumn('is_public', 1)
tableSamples.ArrangeColumns(['sample','is_public','sample_context'])
tableSamples.PrintRows(0,9)
print('Count: '+str(tableSamples.GetRowCount()))
tableSamples.SaveFile(basedir+'/Output/sample.txt', True, '')
tableSamples.SaveSQLDump(basedir+'/Output/sample.sql','sample')

