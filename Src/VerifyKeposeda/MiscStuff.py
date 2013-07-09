
import copy
import sys
import gc
from TableUtils import VTTable
from TableUtils import IntervalTools

import numpy


import matplotlib.pyplot as plt
plt.plot([1,2,3,4])
plt.ylabel('some numbers')
plt.show()
sys.exit()



def triv():
    basepath="C:/Data/Articles/PositiveSelection"
    
    popname="fula"
    
    malawiihs=VTTable.VTTable()
    malawiihs.LoadFile(basepath+"/DataPV/SNP/IHS/{0}_Untransmitted_ihs_standardized.txt".format(popname))
    malawiihs.PrintRows(0,10)
    
    filt1=malawiihs.FilterByFunctionReturn(lambda x: x==5,"chromosome")
    filt2=filt1.SortValuesReturn("Pos35")
    filt2.PrintRows(0,10)
    
    filt2.SaveFile(basepath+"/DataPV/SNP/IHS/{0}_ihs_chrom5.txt".format(popname))


    
    
    
class B64:
    def __init__(self):
        self.encodestr="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
        #establish the inversion table:
        self.invencode=[]
        for i in range(0,255): self.invencode.append(0)
        for i in range(len(self.encodestr)):
            self.invencode[ord(self.encodestr[i])]=i;
    
    def Int2B64(self, val, cnt):
        rs=''
        for _ in range(0,cnt):
            rs=self.encodestr[val & 63]+rs
            val=val >> 6
        return rs
    
    def B642Int(self, st):
        rs=0
        for ch in st:
            rs=rs*64+self.invencode[ord(ch)]
        return rs
        
codec=B64()        

val1=9876543
encoded=codec.Int2B64(val1,5)
val2=codec.B642Int(encoded)
print('{0} {1} {2}'.format(val1,val2,encoded))
