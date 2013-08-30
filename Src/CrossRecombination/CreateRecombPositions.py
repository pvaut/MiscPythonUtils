from TableUtils import VTTable
import sys
import numpy

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



