from TableUtils import VTTable
import sys
import matplotlib.pyplot as plt

import MySQLdb


DBSRV = 'localhost'
DBUSER = 'root'
DBPASS = '1234'
BASEDIR = '/users/pvaut/Documents/Genome'
SOURCEDIR = BASEDIR + '/SourceData/sampledata/datasets/PfReconn'
DB='mm6_pfprism'

def LoadSQLTable(tb, tableName, maxRowCount=None):
    db = MySQLdb.connect(host=DBSRV, user=DBUSER, passwd=DBPASS, db=DB, charset='utf8')
    cur = db.cursor()
    whereclause='select {colnames} from {tablename}'.format(
        colnames=', '.join(['`'+vl+'`' for vl in tb.GetColList()]),
        tablename=tableName
    )
    if maxRowCount is not None:
        whereclause += ' LIMIT '+str(maxRowCount)
    print(whereclause)
    cur.execute(whereclause)
    for row in cur.fetchall():
        tb.AddRowEmpty()
        rownr = tb.GetRowCount()-1
        for colnr in range(len(row)):
            tb.SetValue(rownr, colnr, row[colnr])


tbEntities = VTTable.VTTable()
tbEntities.AddColumn(VTTable.VTColumn('id', 'Text'))
tbEntities.AddColumn(VTTable.VTColumn('name', 'Text'))
LoadSQLTable(tbEntities, 'entity')
tbEntities.PrintRows(0,10)
mapEntities = tbEntities.BuildColDict('id', False)
def EntityId2Name(id):
    return tbEntities.GetValue(mapEntities[id], 1)


tbSamples = VTTable.VTTable()
tbSamples.AddColumn(VTTable.VTColumn('id', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('source_label', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('seq_label', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('owner', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('collection_date', 'Text'))
tbSamples.AddColumn(VTTable.VTColumn('longitude', 'Value'))
tbSamples.AddColumn(VTTable.VTColumn('latitude', 'Value'))
tbSamples.AddColumn(VTTable.VTColumn('location_accuracy', 'Value'))
tbSamples.AddColumn(VTTable.VTColumn('inferred_coordinates', 'Text'))
LoadSQLTable(tbSamples, 'sample')
tbSamples.MapCol('owner', EntityId2Name)
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

sMetaKeys = ['Set', 'method', 'country', 'region', 'PI', 'contact', 'Barcode scan location', 'supplier', 'sequenom', 'reported', 'internal']
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
tbSamples.SaveFile(SOURCEDIR+'/datatables/samples/data')





################### Import assay info
tbAssays = VTTable.VTTable()
tbAssays.AddColumn(VTTable.VTColumn('id', 'Text'))
tbAssays.AddColumn(VTTable.VTColumn('label', 'Text'))
tbAssays.AddColumn(VTTable.VTColumn('allele1', 'Text'))
tbAssays.AddColumn(VTTable.VTColumn('allele2', 'Text'))
tbAssays.AddColumn(VTTable.VTColumn('pf_chr_214', 'Text'))
tbAssays.AddColumn(VTTable.VTColumn('pf_pos_214', 'Value'))
tbAssays.AddColumn(VTTable.VTColumn('pf_chr_30', 'Text'))
tbAssays.AddColumn(VTTable.VTColumn('pf_pos_30', 'Value'))
tbAssays.AddColumn(VTTable.VTColumn('gene', 'Text'))
#pf_chr_214 | pf_pos_214 | pf_chr_30 | pf_pos_30 | gene
LoadSQLTable(tbAssays, 'assay')
tbAssays.PrintRows(0, 10)
mapAssays = tbAssays.BuildColDict('id', False)
tbAssays.saveheadertype = False
tbAssays.SaveFile(SOURCEDIR+'/datatables/assays/data')



################### Import sample x assay info
tbCallsOrig = VTTable.VTTable()
tbCallsOrig.AddColumn(VTTable.VTColumn('sample', 'Text'))
tbCallsOrig.AddColumn(VTTable.VTColumn('assay', 'Text'))
tbCallsOrig.AddColumn(VTTable.VTColumn('params', 'Value'))
tbCallsOrig.AddColumn(VTTable.VTColumn('call', 'Text'))
#pf_chr_214 | pf_pos_214 | pf_chr_30 | pf_pos_30 | gene
LoadSQLTable(tbCallsOrig, 'stored_vw_snpcalls', None)
tbCallsOrig.PrintRows(0, 10)


tbCallsProcessed = VTTable.VTTable()
tbCallsProcessed.AddColumn(VTTable.VTColumn('sample_id', 'Text'))
tbCallsProcessed.AddColumn(VTTable.VTColumn('assay_id', 'Text'))
tbCallsProcessed.AddColumn(VTTable.VTColumn('assay_label', 'Text'))
tbCallsProcessed.AddColumn(VTTable.VTColumn('call_default', 'Text'))
tbCallsProcessed.AddColumn(VTTable.VTColumn('call_manual', 'Text'))
tbCallsProcessed.AddColumn(VTTable.VTColumn('call_improved', 'Text'))
tbCallsProcessed.AddColumn(VTTable.VTColumn('call_overall', 'Text'))
tbCallsProcessed.AddColumn(VTTable.VTColumn('call_illumina', 'Text'))

colnr_sampleid = tbCallsOrig.GetColNr('sample')
colnr_assayid = tbCallsOrig.GetColNr('assay')
colnr_params = tbCallsOrig.GetColNr('params')
colnr_call = tbCallsOrig.GetColNr('call')
mapCalls = {}
for rownr in tbCallsOrig.GetRowNrRange():
    sampleid = tbCallsOrig.GetValue(rownr, colnr_sampleid)
    assayid = tbCallsOrig.GetValue(rownr, colnr_assayid)
    param = tbCallsOrig.GetValue(rownr, colnr_params)
    call = tbCallsOrig.GetValue(rownr, colnr_call)
    rownr_sample = mapSamples[sampleid]
    ok = True
    if assayid not in mapAssays:
        print('ERROR: Invalid sample id '+str(sampleid))
        ok = False
    if ok:
        rownr_assay = mapAssays[assayid]
        callid =str(sampleid)+'_'+str(assayid)
        if callid not in mapCalls:
            tbCallsProcessed.AddRowEmpty()
            rownr_call = tbCallsProcessed.GetRowCount()-1
            tbCallsProcessed.SetValue(rownr_call, 0, sampleid)
            tbCallsProcessed.SetValue(rownr_call, 1, assayid)
            tbCallsProcessed.SetValue(rownr_call, 2, tbAssays.GetValue(rownr_assay, tbAssays.GetColNr('label')))
            mapCalls[callid] = rownr_call
        rownr_call = mapCalls[callid]
        if param == 1:
            tbCallsProcessed.SetValue(rownr_call,3, call)
        if param == 2:
            tbCallsProcessed.SetValue(rownr_call,4, call)
        if param == 3:
            tbCallsProcessed.SetValue(rownr_call,5, call)


# Read & add Illumina calls
################### Import sample x assay info
tbCallsIllumina = VTTable.VTTable()
tbCallsIllumina.AddColumn(VTTable.VTColumn('sample', 'Text'))
tbCallsIllumina.AddColumn(VTTable.VTColumn('assay', 'Text'))
tbCallsIllumina.AddColumn(VTTable.VTColumn('illumina_call', 'Text'))
LoadSQLTable(tbCallsIllumina, 'z_illumina_calls', None)
tbCallsIllumina.PrintRows(0, 10)
for rownr in tbCallsIllumina.GetRowNrRange():
    sampleid = tbCallsIllumina.GetValue(rownr, 0)
    assayid = tbCallsIllumina.GetValue(rownr, 1)
    call = tbCallsIllumina.GetValue(rownr, 2)
    rownr_sample = mapSamples[sampleid]
    ok = True
    if assayid not in mapAssays:
        print('ERROR: Invalid sample id '+str(sampleid))
        ok = False
    if ok:
        rownr_assay = mapAssays[assayid]
        callid =str(sampleid)+'_'+str(assayid)
        if callid not in mapCalls:
            tbCallsProcessed.AddRowEmpty()
            rownr_call = tbCallsProcessed.GetRowCount()-1
            tbCallsProcessed.SetValue(rownr_call, 0, sampleid)
            tbCallsProcessed.SetValue(rownr_call, 1, assayid)
            tbCallsProcessed.SetValue(rownr_call, 2, tbAssays.GetValue(rownr_assay, tbAssays.GetColNr('label')))
            mapCalls[callid] = rownr_call
        rownr_call = mapCalls[callid]
        tbCallsProcessed.SetValue(rownr_call, 7, call)


tbCallsProcessed.PrintRows(0,10)
tbCallsProcessed.saveheadertype = False
tbCallsProcessed.SaveFile(SOURCEDIR+'/datatables/calls/data')
