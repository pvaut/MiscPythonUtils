from TableUtils import VTTable
import sys
import matplotlib.pyplot as plt

import MySQLdb


DBSRV = 'localhost'
DBUSER = 'root'
DBPASS = '1234'
BASEDIR = '/home/pvaut/Documents/Genome'
DB='mm6_pfprism'

def LoadSQLTable(tb, tableName):
    db = MySQLdb.connect(host=DBSRV, user=DBUSER, passwd=DBPASS, db=DB, charset='utf8')
    cur = db.cursor()
    whereclause='select {colnames} from {tablename}'.format(
        colnames=', '.join(['`'+vl+'`' for vl in tb.GetColList()]),
        tablename=tableName
    )
    print(whereclause)
    cur.execute(whereclause)
    for row in cur.fetchall():
        tb.AddRowEmpty()
        rownr = tb.GetRowCount()-1
        for colnr in range(len(row)):
            tb.SetValue(rownr, colnr, row[colnr])


tbSamples = VTTable.VTTable()
tbSamples.AddColumn(VTTable.VTColumn('id', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('source_label', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('seq_label', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('collection_date', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('longitude', 'Value'))
tbSamples.AddColumn(VTTable.VTColumn('latitude', 'Value'))
tbSamples.AddColumn(VTTable.VTColumn('location_accuracy', 'Value'))
tbSamples.AddColumn(VTTable.VTColumn('inferred_coordinates', 'Text'))
LoadSQLTable(tbSamples, 'sample')
tbSamples.PrintRows(0,10)
mapSamples = tbSamples.BuildColDict('id', False)


def parseDate(str):
    if str is None:
        return None
    str2 = str[0:4]+'-'+str[4:6]+'-'+str[6:8]
#    print('===='+str+'===='+str2)
    return str2

def None2Empty(str):
    if str is None:
        return ''
    else:
        return str

tbSamples.MapCol('collection_date', parseDate)


tbSampleMeta = VTTable.VTTable()
tbSampleMeta.AddColumn(VTTable.VTColumn('sample_id', 'Text'))
tbSampleMeta.AddColumn(VTTable.VTColumn('key', 'Text'))
tbSampleMeta.AddColumn(VTTable.VTColumn('value', 'Text'))
tbSmpMt_ColNrSample = tbSampleMeta.GetColNr('sample_id')
tbSmpMt_ColNrKey = tbSampleMeta.GetColNr('key')
tbSmpMt_ColNrValue = tbSampleMeta.GetColNr('value')
LoadSQLTable(tbSampleMeta, 'vw_metadata')
tbSampleMeta.ConvertToAscii('value')
tbSampleMeta.PrintRows(0, 10)

sMetaKeys = ['Set', 'method', 'country', 'region', 'Barcode scan location', 'supplier', 'sequenom', 'reported', 'internal']
mapMetaKeys = {}

for metaKey in sMetaKeys:
    tbSamples.AddColumn(VTTable.VTColumn(metaKey, 'Text'))
    tbSamples.FillColumn(metaKey, '')
    colnr = tbSamples.GetColNr(metaKey)
    mapMetaKeys[metaKey] = colnr
    # for rownr in tbSamples.GetRowNrRange():
    #     tbSamples.SetValue(rownr, colnr, '')
for rownr in tbSampleMeta.GetRowNrRange():
    sampleid = tbSampleMeta.GetValue(rownr, tbSmpMt_ColNrSample)
    key = tbSampleMeta.GetValue(rownr, tbSmpMt_ColNrKey)
    content = tbSampleMeta.GetValue(rownr, tbSmpMt_ColNrValue)
    if sampleid is not None:
        if sampleid not in mapSamples:
            print('Missing sample '+sampleid)
        if key in mapMetaKeys:
            tbSamples.SetValue(mapSamples[sampleid], mapMetaKeys[key], content)

tbSamples.RenameCol('Set', 'MTSet')
tbSamples.RenameCol('method', 'MTMethod')
tbSamples.RenameCol('country', 'MTCountry')
tbSamples.RenameCol('region', 'MTRegion')
tbSamples.RenameCol('Barcode scan location', 'MTBarcodeScanLocation')
tbSamples.RenameCol('supplier', 'MTSupplier')
tbSamples.RenameCol('sequenom', 'MTSequenom')
tbSamples.RenameCol('reported', 'MTReported')
tbSamples.RenameCol('internal', 'MTInternal')

tbSamples.MapCol('collection_date', None2Empty)
tbSamples.MapCol('longitude', None2Empty)
tbSamples.MapCol('latitude', None2Empty)
tbSamples.MapCol('location_accuracy', None2Empty)

tbSamples.PrintRows(0, 10)

tbSamples.saveheadertype = False
tbSamples.SaveFile(BASEDIR+'/SourceData/datasets/PfReconn/datatables/samples/data')