from TableUtils import VTTable
import sys
#import numpy


# #TMP
#
# tb = VTTable.VTTable()
# tb.allColumnsText = True
# tb.LoadFile('/Users/pvaut/Documents/Genome/PGV301/AlleleFreq-nraf.tab')
# tb.PrintRows(0,10)
#
# dupls = tb.GetDuplicateValues('SnpName')
# print('Duplicates: '+str(dupls))
#
#
# sys.exit()
#
# #TMP
# samples = "AB0102-C	AB0125-C	AB0149-C	AB0152-C	AB0163-C	AB0168-C	AB0245-C	AJ0023-C	AJ0024-C	AJ0025-C	AJ0026-C	AJ0027-C	AJ0029-C	AJ0030-C	AJ0032-C	AJ0033-C	AJ0035-C	AJ0036-C	AJ0039-C	AJ0040-C	AJ0041-C	AJ0042-C	AJ0043-C	AJ0046-C	AJ0047-C	AJ0051-C	AJ0052-C	AJ0055-C	AJ0056-C	AJ0058-C	AJ0061-C	AJ0063-C	AJ0065-C	AJ0072-C	AJ0073-C	AJ0074-C	AJ0077-C	AJ0079-C	AJ0081-C	AJ0082-C	AJ0083-C	AJ0084-C	AJ0085-C	AJ0086-C	AJ0088-C	AJ0090-C	AJ0091-C	AJ0103-C	AJ0105-C	AJ0108-C	AJ0109-C	AJ0110-C	AJ0111-C	AJ0112-C	AJ0114-C	AJ0115-C	AK0059-C	AK0064-C	AK0111-C	AK0113-C	AK0114-C	AK0115-C	AK0116-C	AK0118-C	AK0119-C	AK0120-C	AK0122-C	AN0052-C	AR0003-C	AR0005-C	AR0025-C	AR0026-C	AR0028-C	AR0029-C	AR0030-C	AR0031-C	AR0032-C	AR0033-C	AR0037-C	AR0039-C	AR0053-C	AR0056-C	AS0042-C	AS0050-C	AS0052-C	AS0063-C	AV0016-C	AV0019-C"
# samples = samples.split('\t')
# fp=open('/home/pvaut/tmp/samples2','w')
# for sample in samples:
#     fp.write(sample+'\t1\n')
# fp.close()
# print(str(samples))
# sys.exit()

crosses = ['3d7_hb3', 'hb3_dd2', '7g8_gb4']

crossInfo = {}
for cross in crosses:
    crossInfo[cross]={
        'positlist':[],
        'positmap':{}
    }


tb=VTTable.VTTable()
tb.allColumnsText=True
tb.LoadFile('posits.txt')
tb.ConvertColToValue('pos_mid')
tb.RenameCol('pos_mid','pos')

tb.DropCol('pos_min')
tb.DropCol('pos_max')
tb.DropCol('pos_range')
tb.DropCol('sample')
#tb.DropCol('cross')

tbcol_chrom=tb.GetColNr('chrom')
tbcol_pos=tb.GetColNr('pos')
tbcol_cross=tb.GetColNr('cross')

tb.PrintRows(0,6)

for rownr in tb.GetRowNrRange():
    cross=crossInfo[tb.GetValue(rownr,tbcol_cross)]
    positstr=tb.GetValue(rownr,tbcol_chrom)+':'+str(tb.GetValue(rownr,tbcol_pos))
    if positstr not in cross['positmap']:
        cross['positmap'][positstr]=0
        cross['positlist'].append(positstr)
    cross['positmap'][positstr] += 1


fp=open('recombinationpositions','w')
fp.write('chrom#T\tpos\tcrossid#T\tsamplecount\n')
for crossid in crossInfo:
    cross=crossInfo[crossid]
    for positstr in cross['positlist']:
        fp.write('{0}\t{1}\t{2}\t{3}\n'.format(positstr.split(':')[0],positstr.split(':')[1],crossid,cross['positmap'][positstr]))
fp.close()
tb=VTTable.VTTable()
tb.allColumnsText=True
tb.LoadFile('recombinationpositions')
tb.PrintRows(0,10)
tb.SaveSQLCreation('recombinationpositions_create.sql','recombinationpositions')
tb.SaveSQLDump('recombinationpositions_dump.sql','recombinationpositions')



