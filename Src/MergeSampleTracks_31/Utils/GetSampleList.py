import config
import VTTable
import os
import gzip

def GetSampleList(pattern):

    tb = VTTable.VTTable()
    tb.allColumnsText = True

    tb.LoadFile(os.path.join(config.basedir, 'samplesReport31.txt'))

    tb.PrintRows(0,10)

    lst =[]
    cnt = 0
    for rownr in range(tb.GetRowCount()):
        if tb.GetValue(rownr,tb.GetColNr('Exclude')) == 'FALSE':
            sample = tb.GetValue(rownr,tb.GetColNr('Sample'))
            study = tb.GetValue(rownr,tb.GetColNr('Study'))
            study = study.replace('-', '_')
            filename = study + '/' + pattern.format(id=sample)
            lst.append(filename)
	    cnt += 1
	    if (config.maxsamplecount>0) and (cnt>=config.maxsamplecount):
		break
    return lst


# lst = GetSampleList('{id}.coverage.txt.gz')
#
# for filename in lst:
#     print(filename)
#     with open(os.path.join(config.basedir, 'pysamstats', filename)) as fp:
#         for line in fp:
#             pass
