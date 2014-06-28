from TableUtils import VTTable
import sys
#import matplotlib.pyplot as plt
import MySQLdb
import unidecode
import GeoTools

# TODO: fetch from ftp://ftp.sanger.ac.uk/pub/teams/112/static/n8crwy38nh.zip



DBSRV = 'localhost'
DBUSER = 'root'
DBPASS = '1234'
BASEDIR = '/home/pvaut/Documents/Genome'
SOURCEDIR = BASEDIR + '/SourceData/datasets/PfReconn'
DB='mm6_pfprism'
limit = 10000000000# !!!

# def LoadSQLTable(tb, tableName, maxRowCount=None):
#     db = MySQLdb.connect(host=DBSRV, user=DBUSER, passwd=DBPASS, db=DB, charset='utf8')
#     cur = db.cursor()
#     whereclause='select {colnames} from {tablename} limit {limit}'.format(
#         colnames=', '.join(['`'+vl+'`' for vl in tb.GetColList()]),
#         tablename=tableName,
#         limit=limit
#     )
#     if maxRowCount is not None:
#         whereclause += ' LIMIT '+str(maxRowCount)
#     print(whereclause)
#     cur.execute(whereclause)
#     for row in cur.fetchall():
#         tb.AddRowEmpty()
#         rownr = tb.GetRowCount()-1
#         for colnr in range(len(row)):
#             content = row[colnr]
#             if content is not None:
#                 if isinstance(content, (int, long, float)):
#                     content = str(content)
#                 else:
#                     content = unidecode.unidecode(content)
#             tb.SetValue(rownr, colnr, content)


tbEntities = VTTable.VTTable()
tbEntities.allColumnsText = True
tbEntities.LoadFile(BASEDIR+'/PfReconn/entity.tab', limit)
tbEntities.ArrangeColumns(['id', 'name'])
# tbEntities.AddColumn(VTTable.VTColumn('id', 'Text'))
# tbEntities.AddColumn(VTTable.VTColumn('name', 'Text'))
# LoadSQLTable(tbEntities, 'entity')
tbEntities.PrintRows(0,10)
mapEntities = tbEntities.BuildColDict('id', False)
def EntityId2Name(id):
    return tbEntities.GetValue(mapEntities[id], 1)



tbSamples = VTTable.VTTable()
tbSamples.allColumnsText = True
tbSamples.LoadFile(BASEDIR+'/PfReconn/sample.tab', limit)
tbSamples.ArrangeColumns(['id', 'source_label', 'seq_label', 'owner', 'collection_date', 'dna_extraction_date', 'genotype_date', 'longitude', 'latitude', 'location_accuracy', 'inferred_coordinates', 'country_iso', 'region'])
# tbSamples.AddColumn(VTTable.VTColumn('id', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('source_label', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('seq_label', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('owner', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('collection_date', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('dna_extraction_date', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('genotype_date', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('longitude', 'Value'))
# tbSamples.AddColumn(VTTable.VTColumn('latitude', 'Value'))
# tbSamples.AddColumn(VTTable.VTColumn('location_accuracy', 'Value'))
# tbSamples.AddColumn(VTTable.VTColumn('inferred_coordinates', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('country_iso', 'Text'))
# tbSamples.AddColumn(VTTable.VTColumn('region', 'Text'))
# LoadSQLTable(tbSamples, 'sample')
tbSamples.MapCol('owner', EntityId2Name)
tbSamples.PrintRows(0,10)
mapSamples = tbSamples.BuildColDict('id', False)

def parseDate(str):
    if str is None:
        return ''
    str2 = str[0:4]+'-'+str[4:6]+'-'+str[6:8]
#    print('===='+str+'===='+str2)
    return str2

def None2Empty(str):
    if str is None:
        return ''
    else:
        return str

tbSamples.MapCol('country_iso', None2Empty)
tbSamples.MapCol('region', None2Empty)
tbSamples.MapCol('location_accuracy', None2Empty)


tbSamples.MapCol('collection_date', parseDate)
tbSamples.MapCol('dna_extraction_date', parseDate)
tbSamples.MapCol('genotype_date', parseDate)

tbSamples.PrintRows(0, 10)

geoData = []
for rownr in tbSamples.GetRowNrRange():
    id = tbSamples.GetValue(rownr,tbSamples.GetColNr('id'))
    longit = tbSamples.GetValue(rownr,tbSamples.GetColNr('longitude'))
    latit = tbSamples.GetValue(rownr,tbSamples.GetColNr('latitude'))
    if (longit != '') and (latit != ''):
        geoData.append({
            'id': id,
            'longit': float(longit),
            'latit': float(latit)
        })
tbSamples.MapCol('longitude', None2Empty)
tbSamples.MapCol('latitude', None2Empty)
GeoTools.Aggregate(geoData, 2)

idx = tbSamples.BuildColDict('id', False)
for pt in geoData:
    rownr = idx[pt['id']]
    tbSamples.SetValue(rownr, tbSamples.GetColNr('longitude'), pt['longit'])
    tbSamples.SetValue(rownr, tbSamples.GetColNr('latitude'), pt['latit'])



tbSampleMeta = VTTable.VTTable()
tbSampleMeta.allColumnsText = True
tbSampleMeta.LoadFile(BASEDIR+'/PfReconn/vw_metadata.tab', limit)
tbSampleMeta.ArrangeColumns(['sample_id', 'key', 'value'])
# tbSampleMeta.AddColumn(VTTable.VTColumn('sample_id', 'Text'))
# tbSampleMeta.AddColumn(VTTable.VTColumn('key', 'Text'))
# tbSampleMeta.AddColumn(VTTable.VTColumn('value', 'Text'))
tbSmpMt_ColNrSample = tbSampleMeta.GetColNr('sample_id')
tbSmpMt_ColNrKey = tbSampleMeta.GetColNr('key')
tbSmpMt_ColNrValue = tbSampleMeta.GetColNr('value')
# LoadSQLTable(tbSampleMeta, 'vw_metadata')
tbSampleMeta.ConvertToAscii('value')
tbSampleMeta.PrintRows(0, 10)

sMetaKeys = ['Set', 'method', 'country', 'region', 'PI', 'contact', 'Barcode scan location', 'supplier', 'sequenom', 'reported', 'internal']
mapMetaKeys = {}

for metaKey in sMetaKeys:
    colName = 'MT' + metaKey.replace(' ', '')
    tbSamples.AddColumn(VTTable.VTColumn(colName, 'Text'))
    tbSamples.FillColumn(colName, '')
    colnr = tbSamples.GetColNr(colName)
    mapMetaKeys[metaKey] = colnr
    # for rownr in tbSamples.GetRowNrRange():
    #     tbSamples.SetValue(rownr, colnr, '')
for rownr in tbSampleMeta.GetRowNrRange():
    sampleid = tbSampleMeta.GetValue(rownr, tbSmpMt_ColNrSample)
    key = tbSampleMeta.GetValue(rownr, tbSmpMt_ColNrKey)
    content = tbSampleMeta.GetValue(rownr, tbSmpMt_ColNrValue)
    if sampleid is not None:
        if sampleid not in mapSamples:
            print('Missing sample '+sampleid+';'+key+';'+content)
        else:
            if key in mapMetaKeys:
                prevContent = tbSamples.GetValue(mapSamples[sampleid], mapMetaKeys[key])
                if len(prevContent) > 0:
                    content = prevContent + ';' + content
                    print('MULTIPLE KEY VALUES: '+sampleid+';'+key+'='+content)
                tbSamples.SetValue(mapSamples[sampleid], mapMetaKeys[key], content)

# tbSamples.RenameCol('Set', 'MTSet')
# tbSamples.RenameCol('method', 'MTMethod')
# tbSamples.RenameCol('country', 'MTCountry')
# tbSamples.RenameCol('region', 'MTRegion')
# tbSamples.RenameCol('Barcode scan location', 'MTBarcodeScanLocation')
# tbSamples.RenameCol('supplier', 'MTSupplier')
# tbSamples.RenameCol('sequenom', 'MTSequenom')
# tbSamples.RenameCol('reported', 'MTReported')
# tbSamples.RenameCol('internal', 'MTInternal')






################### Import assay info
tbAssays = VTTable.VTTable()
tbAssays.allColumnsText = True
tbAssays.LoadFile(BASEDIR+'/PfReconn/assay.tab', limit)
tbAssays.ArrangeColumns(['id', 'label', 'allele1', 'allele2', 'pf_chr_214', 'pf_pos_214', 'pf_chr_30', 'pf_pos_30', 'gene'])
# tbAssays.AddColumn(VTTable.VTColumn('id', 'Text'))
# tbAssays.AddColumn(VTTable.VTColumn('label', 'Text'))
# tbAssays.AddColumn(VTTable.VTColumn('allele1', 'Text'))
# tbAssays.AddColumn(VTTable.VTColumn('allele2', 'Text'))
# tbAssays.AddColumn(VTTable.VTColumn('pf_chr_214', 'Text'))
# tbAssays.AddColumn(VTTable.VTColumn('pf_pos_214', 'Value'))
# tbAssays.AddColumn(VTTable.VTColumn('pf_chr_30', 'Text'))
# tbAssays.AddColumn(VTTable.VTColumn('pf_pos_30', 'Value'))
# tbAssays.AddColumn(VTTable.VTColumn('gene', 'Text'))
#pf_chr_214 | pf_pos_214 | pf_chr_30 | pf_pos_30 | gene
# LoadSQLTable(tbAssays, 'assay')
tbAssays.MapCol('gene', None2Empty)

tbAssaysExtra = VTTable.VTTable()
tbAssaysExtra.allColumnsText = True
tbAssaysExtra.LoadFile(BASEDIR+'/PfReconn/AssayMetaData.txt', limit)
tbAssaysExtra.DropCol("label")
tbAssaysExtra.DropCol("allele1")
tbAssaysExtra.DropCol("allele2")
tbAssaysExtra.DropCol("pf_chr_214")
tbAssaysExtra.DropCol("pf_pos_214")
tbAssaysExtra.DropCol("pf_chr_30")
tbAssaysExtra.DropCol("pf_pos_30")
tbAssaysExtra.DropCol("gene")
tb = VTTable.VTTable()
tb.MergeTablesByKeyFrom(tbAssays, tbAssaysExtra, 'id', True, False)
tbAssays = tb


def ChromNr2Name(nr):
    if nr is None:
        return ''
    nr = str(nr)
    if len(nr)<2:
        nr = '0' + nr
    return "Pf3D7_"+nr+"_v3"
tbAssays.MapCol('pf_chr_30', ChromNr2Name)

tbAssays.PrintRows(0, 1000)
mapAssays = tbAssays.BuildColDict('id', False)


################### Import sample x assay info
tbCallsOrig = VTTable.VTTable()
tbCallsOrig.allColumnsText = True
tbCallsOrig.LoadFile(BASEDIR+'/PfReconn/vw_snpcalls.tab', limit)
tbCallsOrig.ArrangeColumns(['sample', 'assay', 'params', 'call'])
# tbCallsOrig.AddColumn(VTTable.VTColumn('sample', 'Text'))
# tbCallsOrig.AddColumn(VTTable.VTColumn('assay', 'Text'))
# tbCallsOrig.AddColumn(VTTable.VTColumn('params', 'Value'))
# tbCallsOrig.AddColumn(VTTable.VTColumn('call', 'Text'))
# #pf_chr_214 | pf_pos_214 | pf_chr_30 | pf_pos_30 | gene
# LoadSQLTable(tbCallsOrig, 'stored_vw_snpcalls', None)
tbCallsOrig.MapCol('call', None2Empty)
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
        if int(param) == 1:
            tbCallsProcessed.SetValue(rownr_call,3, call)
        if int(param) == 2:
            tbCallsProcessed.SetValue(rownr_call,4, call)
        if int(param) == 3:
            tbCallsProcessed.SetValue(rownr_call,5, call)


# Read & add Illumina calls
################### Import sample x assay info
tbCallsIllumina = VTTable.VTTable()
tbCallsIllumina.allColumnsText = True
tbCallsIllumina.LoadFile(BASEDIR+'/PfReconn/z_illumina_calls.tab', limit)
tbCallsIllumina.ArrangeColumns(['sample', 'assay', 'illumina_call'])
# tbCallsIllumina.AddColumn(VTTable.VTColumn('sample', 'Text'))
# tbCallsIllumina.AddColumn(VTTable.VTColumn('assay', 'Text'))
# tbCallsIllumina.AddColumn(VTTable.VTColumn('illumina_call', 'Text'))
# LoadSQLTable(tbCallsIllumina, 'z_illumina_calls', None)
tbCallsIllumina.MapCol('illumina_call', None2Empty)
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



print('DETERMINING SAMPLE CALL STATS...')

sampleData = {}
for rownr in tbSamples.GetRowNrRange():
    sampleData[tbSamples.GetValue(rownr, 0)] = {
        'assay_sq_count': 0,
        'assay_sq_water': 0,
        'assay_sq_mixed': 0,
        'assay_sq_nonref': 0,
        'assay_il_count': 0,
        'assay_il_missing': 0,
        'assay_il_mixed': 0,
        'assay_both_count': 0,
        'assay_both_conform': 0,
    }

for rownr in tbCallsProcessed.GetRowNrRange():
    sampleid = tbCallsProcessed.GetValue(rownr, 0)
#    assayid = tbCallsProcessed.GetValue(rownr, 1)
    callsq = tbCallsProcessed.GetValue(rownr, 5)
    callil = tbCallsProcessed.GetValue(rownr, 7)
    sampleInfo = sampleData[sampleid]
    if callsq:
        sampleInfo['assay_sq_count'] += 1
        if callsq == 'W':
            sampleInfo['assay_sq_water'] += 1
        if callsq == 'M':
            sampleInfo['assay_sq_mixed'] += 1

    if callil:
        sampleInfo['assay_il_count'] += 1
        if callil == 'M':
            sampleInfo['assay_il_mixed'] += 1
        if callil == '-':
            sampleInfo['assay_il_missing'] += 1

    if callil and callsq:
        if (callsq in ['A', 'C', 'G', 'T']) and (callil in ['A', 'C', 'G', 'T']):
            sampleInfo['assay_both_count'] += 1
            if callil == callsq:
                sampleInfo['assay_both_conform'] += 1

#    if callsq is not None and callill is not None:
#        print('{0} {1} {2} {3}'.format(sampleid,assayid,callsq,callill))



tbSamples.AddColumn(VTTable.VTColumn('SQAssayCount', 'Value'))
tbSamples.FillColumn('SQAssayCount', 0)
tbSamples.AddColumn(VTTable.VTColumn('SQAssayWaterFrac', 'Value'))
tbSamples.FillColumn('SQAssayWaterFrac', None)
tbSamples.AddColumn(VTTable.VTColumn('SQAssayMixedFrac', 'Value'))
tbSamples.FillColumn('SQAssayMixedFrac', None)
tbSamples.AddColumn(VTTable.VTColumn('ILAssayCount', 'Value'))
tbSamples.FillColumn('ILAssayCount', 0)
tbSamples.AddColumn(VTTable.VTColumn('ILAssayMixedFrac', 'Value'))
tbSamples.FillColumn('ILAssayMixedFrac', None)
tbSamples.AddColumn(VTTable.VTColumn('ILAssayMissingFrac', 'Value'))
tbSamples.FillColumn('ILAssayMissingFrac', None)
tbSamples.AddColumn(VTTable.VTColumn('ILAssayDiscordFrac', 'Value'))
tbSamples.FillColumn('ILAssayDiscordFrac', None)

for rownr in tbSamples.GetRowNrRange():
    sampleid = tbSamples.GetValue(rownr, 0)
    sampleInfo = sampleData[sampleid]
    # sq data
    assaycount = sampleInfo['assay_sq_count']
    tbSamples.SetValue(rownr, tbSamples.GetColNr('SQAssayCount'), assaycount)
    if assaycount > 0:
        tbSamples.SetValue(rownr, tbSamples.GetColNr('SQAssayWaterFrac'), sampleInfo['assay_sq_water']*100.0/assaycount)
        tbSamples.SetValue(rownr, tbSamples.GetColNr('SQAssayMixedFrac'), sampleInfo['assay_sq_mixed']*100.0/assaycount)
    #ill data
    assaycount = sampleInfo['assay_il_count']
    tbSamples.SetValue(rownr, tbSamples.GetColNr('ILAssayCount'), assaycount)
    if assaycount > 0:
        tbSamples.SetValue(rownr, tbSamples.GetColNr('ILAssayMixedFrac'), sampleInfo['assay_il_mixed']*100.0/assaycount)
        tbSamples.SetValue(rownr, tbSamples.GetColNr('ILAssayMissingFrac'), sampleInfo['assay_il_missing']*100.0/assaycount)
    if sampleInfo['assay_both_count'] > 0:
        tbSamples.SetValue(rownr, tbSamples.GetColNr('ILAssayDiscordFrac'), 100.0-sampleInfo['assay_both_conform']*100.0/sampleInfo['assay_both_count'])


tbSamples.PrintRows(0,20)
tbSamples.saveheadertype = False
tbSamples.SaveFile(SOURCEDIR+'/datatables/samples/data')



print('DETERMINING ASSAY CALL STATS...')

assayData = {}
for rownr in tbAssays.GetRowNrRange():
    assayData[tbAssays.GetValue(rownr, 0)] = {
        'sample_sq_count': 0,
        'sample_sq_water': 0,
        'sample_sq_mixed': 0,
        'sample_sq_hascall': 0,
        'sample_sq_nonref': 0,
        'sample_il_count': 0,
        'sample_il_missing': 0,
        'sample_il_mixed': 0,
        'sample_both_count': 0,
        'sample_both_conform': 0,
        'ref': tbAssays.GetValue(rownr,'allele1'),
        'alt': tbAssays.GetValue(rownr,'allele2')
    }

for rownr in tbCallsProcessed.GetRowNrRange():
    assayid = tbCallsProcessed.GetValue(rownr, 1)
    callsq = tbCallsProcessed.GetValue(rownr, 5)
    callil = tbCallsProcessed.GetValue(rownr, 7)
    assayInfo = assayData[assayid]
    if callsq:
        assayInfo['sample_sq_count'] += 1
        if callsq == 'W':
            assayInfo['sample_sq_water'] += 1
        if callsq == 'M':
            assayInfo['sample_sq_mixed'] += 1
        if (callsq == assayInfo['ref']) or (callsq == assayInfo['alt']):
            assayInfo['sample_sq_hascall'] += 1
            if callsq == assayInfo['alt']:
                assayInfo['sample_sq_nonref'] += 1

    if callil:
        assayInfo['sample_il_count'] += 1
        if callil == 'M':
            assayInfo['sample_il_mixed'] += 1
        if callil == '-':
            assayInfo['sample_il_missing'] += 1

    if callil and callsq:
        if (callsq in ['A', 'C', 'G', 'T']) and (callil in ['A', 'C', 'G', 'T']):
            assayInfo['sample_both_count'] += 1
            if callil == callsq:
                assayInfo['sample_both_conform'] += 1

tbAssays.AddColumn(VTTable.VTColumn('SQSampleCount', 'Value'))
tbAssays.FillColumn('SQSampleCount', 0)
tbAssays.AddColumn(VTTable.VTColumn('SQSampleWaterFrac', 'Value'))
tbAssays.FillColumn('SQSampleWaterFrac', None)
tbAssays.AddColumn(VTTable.VTColumn('SQSampleMixedFrac', 'Value'))
tbAssays.FillColumn('SQSampleMixedFrac', None)
tbAssays.AddColumn(VTTable.VTColumn('SQSampleNonrefFrac', 'Value'))
tbAssays.FillColumn('SQSampleNonrefFrac', None)
tbAssays.AddColumn(VTTable.VTColumn('ILSampleCount', 'Value'))
tbAssays.FillColumn('ILSampleCount', 0)
tbAssays.AddColumn(VTTable.VTColumn('ILSampleMixedFrac', 'Value'))
tbAssays.FillColumn('ILSampleMixedFrac', None)
tbAssays.AddColumn(VTTable.VTColumn('ILSampleMissingFrac', 'Value'))
tbAssays.FillColumn('ILSampleMissingFrac', None)
tbAssays.AddColumn(VTTable.VTColumn('ILSampleDiscordFrac', 'Value'))
tbAssays.FillColumn('ILSampleDiscordFrac', None)

for rownr in tbAssays.GetRowNrRange():
    assayid = tbAssays.GetValue(rownr, 0)
    assayInfo = assayData[assayid]
    # sq data
    samplecount = assayInfo['sample_sq_count']
    tbAssays.SetValue(rownr, tbAssays.GetColNr('SQSampleCount'), samplecount)
    if samplecount > 0:
        tbAssays.SetValue(rownr, tbAssays.GetColNr('SQSampleWaterFrac'), assayInfo['sample_sq_water']*100.0/samplecount)
        tbAssays.SetValue(rownr, tbAssays.GetColNr('SQSampleMixedFrac'), assayInfo['sample_sq_mixed']*100.0/samplecount)
        if assayInfo['sample_sq_hascall']>0:
            tbAssays.SetValue(rownr, tbAssays.GetColNr('SQSampleNonrefFrac'), assayInfo['sample_sq_nonref']*100.0/assayInfo['sample_sq_hascall'])
    #ill data
    samplecount = assayInfo['sample_il_count']
    tbAssays.SetValue(rownr, tbAssays.GetColNr('ILSampleCount'), samplecount)
    if samplecount > 0:
        tbAssays.SetValue(rownr, tbAssays.GetColNr('ILSampleMixedFrac'), assayInfo['sample_il_mixed']*100.0/samplecount)
        tbAssays.SetValue(rownr, tbAssays.GetColNr('ILSampleMissingFrac'), assayInfo['sample_il_missing']*100.0/samplecount)
    if assayInfo['sample_both_count']>0:
        tbAssays.SetValue(rownr, tbAssays.GetColNr('ILSampleDiscordFrac'), 100.0-assayInfo['sample_both_conform']*100.0/assayInfo['sample_both_count'])


tbAssays.PrintRows(0, 20)
tbAssays.saveheadertype = False
tbAssays.SaveFile(SOURCEDIR+'/datatables/assays/data')
