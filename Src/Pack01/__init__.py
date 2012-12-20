import sys
import os 
import subprocess
import random
import math

def LoadFile():
    popnames=['YRI','Malawi','Mandinka','Wolof','Fula','Jola','Akan','Northerner']
    popnames_ihs=[x+"_IHS" for x in popnames]
    popnames_xpehh=[x+"_vs_CEU_XPEHH" for x in popnames]
    f = open("C:/Data/Articles/PositiveSelection/DataSaturn/Summary/Windows_XPEHH_IHS_summary_wGenes.txt")
    try:
        header=f.readline()
        header=header.rstrip('\r\n')
        columns=header.split("\t")
        
        ihscols=[]
        xpehhcols=[]
        colnr=0;
        for col in columns:
            if col in popnames_ihs:
                ihscols.append(colnr)
            if col in popnames_xpehh:
                xpehhcols.append(colnr)
            colnr=colnr+1
        print(ihscols)
        print(xpehhcols)
            
        
        print(columns)
        hitcount=0;
        
        for line in f:
            line=line.rstrip('\r\n')
            cells=line.split("\t")
            okihs=True
            nacount=0
            for ihscolnr in ihscols:
                if (cells[ihscolnr]=='NA'): 
                    nacount+=1
                else: 
                    if (float(cells[ihscolnr])>0.01): 
                        okihs=False
            if (nacount==len(ihscols)): okihs=False
            ihs_withna=(nacount>0)
                        
                        
            okxpehh=True
            nacount=0
            for xpcolnr in xpehhcols:
                if (cells[xpcolnr]=='NA'): 
                    nacount+=1
                else: 
                    if (float(cells[xpcolnr])>0.01): 
                        okxpehh=False
            if (nacount==len(xpehhcols)): okxpehh=False
            xpehh_withna=(nacount>0)
                        
            if (okihs or okxpehh):
                print(str(okihs)+"\t"+str(ihs_withna)+'\t'+str(okxpehh)+"\t"+str(xpehh_withna)+"\t"+cells[0]+"\t"+cells[1]+"\t"+cells[2]+"\t"+cells[19])
                hitcount+=1
                
    finally:
        f.close()
        print("Count: "+str(hitcount))
        
    
    
LoadFile()

print("stop")


##rexecpath = os.path.join("test", "bin", "mol2nam")
#
#rexecpath="C:/Software/R/bin/x64/R.exe"
#datapath="C:\\Users\\pvaut\\workspace\\PythonTest01\\" 
# 
#def RunRScript(scriptname): 
##    print(rexecpath)
##    subprocess.call([rexecpath,"--no-save"]) 
##    stdout_text, stderr_text = p.communicate() 
##    return stdout_text.rstrip()
#    #subprocess.call([rexecpath," CMD BATCH C:\\Users\\pvaut\\workspace\\PythonTest01\\RTest01.R"])
#    os.system(rexecpath+" CMD BATCH "+scriptname)
#
#
##runR()
##print("test")
#
#def LoadFile():
#    f = open(datapath+"sample.txt")
#    try:
#        header=f.readline()
#        header=header.rstrip('\r\n')
#        columns=header.split("\t")
#        print(columns)
#        dset=[]
#        for line in f:
#            line=line.rstrip('\r\n')
#            row=[]
#            for cellstring in line.split("\t"):
#                row.append(float(cellstring))
#            dset.append(row)
#    finally:
#        f.close()
#    summed=[]
#    for row in dset:
#        total=0.0
#        for cell in row: total+=cell
#        summed.append(total)
#    print(summed)
#    
#def CreateFile():
#    f = open(datapath+"sample01.txt","w")
#    #f.write("A\tB\n")
#    try:
#        for i in range(0,800):
#            vl=i/30+(i/100)**2+random.random()*i/100
#            f.write(str(i)+"\t"+str(vl)+"\n")
#    finally:
#        f.close()
#
#
#CreateFile()
#RunRScript("C:\\Users\\pvaut\\workspace\\PythonTest01\\RTest01.R")