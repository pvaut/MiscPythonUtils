import copy
import sys
import gc
from TableUtils import VTTable



windowsize=200000


basepath="C:/Data/Articles/PositiveSelection/DataPV"

SnpData=VTTable.VTTable()
#SnpData.LoadFile(basepath+"/SNP/XPEHH/CEU_Fula_650Y_XP_EHH_standardized.txt")
SnpData.LoadFile(basepath+"/SNP/XPEHH/test02.txt")
SnpData.PrintInfo()

colnr_chromo=SnpData.GetColNr('ChromoNr')
colnr_startposit=SnpData.GetColNr('StartPositB35')

def AggregateIDGenerator(Table,RowNr):
    tid=str(Table.GetValue(RowNr,colnr_chromo))
#    tid+="_"
#    tid+=str((int)(Table.GetValue(RowNr,colnr_startposit)/windowsize))
    return(tid)

def SummaryIdentical(lst):
    return(lst[0])

def SummaryGetCount(lst):
    return(len(lst))

def SummaryConcat(lst):
    return(",".join(lst))

def SummaryMax(lst):
    return(max(lst))

def CreateSummaryThresholdCounter(threshold):
    return lambda lst:sum([1 for val in lst if val>=threshold])




AggregateColumns=[]
AggregateColumns.append({'OldColName':'ChromoNr', 'NewColInfo':VTTable.VTColumn('ChromoNr','Text'), 'SummaryFunction':SummaryIdentical })
AggregateColumns.append({'OldColName':'SNP', 'NewColInfo':VTTable.VTColumn('Count','Value'), 'SummaryFunction':SummaryGetCount })
AggregateColumns.append({'OldColName':'SNP', 'NewColInfo':VTTable.VTColumn('SNPS','Text'), 'SummaryFunction':SummaryConcat })
AggregateColumns.append({'OldColName':'XPEHHStandardised', 'NewColInfo':VTTable.VTColumn('Max','Value'), 'SummaryFunction':SummaryMax })

WinData=SnpData.CreateAggregate(AggregateIDGenerator, AggregateColumns)
WinData=WinData.CreateSortValues('Count')

WinData.SaveFile(basepath+"/SNP/XPEHH/rs.txt")