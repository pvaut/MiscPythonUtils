import math
import bisect
import Utils
import sys

basepath="C:/Data/Articles/PositiveSelection/DataSaturn"



windowsize=200000   #!!paper uses 200000
minsnpcount=22      #!! should be 20= 2x11, because each snp is calculated 2 times, for both directions
useabsolutevalue=False
chromocount=22

exportcounts=False
exportmaxval=False
exportavval=False
ranksource='maxval' #!!paper uses 'maxval'

pops=[]


#build start information about what populations to process
apop={}

#pops.append({'name':'YRI',        'files':['CEU_Reference/CEU_YRI_650Y_XP_EHH_standardized.txt']        , 'sign':-1 })
#pops.append({'name':'Malawi',     'files':['CEU_Reference/CEU_Malawi_650Y_XP_EHH_standardized.txt']     , 'sign':-1 })
#pops.append({'name':'Mandinka',   'files':['CEU_Reference/CEU_Mandinka_650Y_XP_EHH_standardized.txt']   , 'sign':-1 })
#pops.append({'name':'Wolof',      'files':['CEU_Reference/CEU_Wolof_650Y_XP_EHH_standardized.txt']      , 'sign':-1 })
#pops.append({'name':'Fula',       'files':['CEU_Reference/CEU_Fula_650Y_XP_EHH_standardized.txt']       , 'sign':-1 })
pops.append({'name':'Jola',       'files':['CEU_Reference/CEU_Jola_650Y_XP_EHH_standardized.txt']       , 'sign':-1 })
#pops.append({'name':'Akan',       'files':['CEU_Reference/CEU_Akan_650Y_XP_EHH_standardized.txt']       , 'sign':-1 })
#pops.append({'name':'Northerner', 'files':['CEU_Reference/CEU_Northerner_650Y_XP_EHH_standardized.txt'] , 'sign':-1 })



#initialise chromosomes & window accumulators
for pop in pops:
    pop['chromosomes']=[]
    for i in range(0,chromocount+1):
        achromo={}
        achromo['windows']=[]
        pop['chromosomes'].append(achromo)


#main loop over all populations
for pop in pops:
    mysign=pop['sign']
    #scan all files associated with this population
    for file in pop['files']:
        f = open(basepath+"/XPEHH/"+file)
        linecount=0;
        for line in f:
            line=line.rstrip('\r\n')
            cells=line.split("\t")
            chromonr=int(cells[0])
            posit=int(cells[2])
            statval=mysign*float(cells[8])
            if (useabsolutevalue):
                statval=math.fabs(statval)
            
            windownr=int(posit/windowsize)
            windowlist=pop['chromosomes'][chromonr]['windows']
            while len(windowlist)<=windownr:#extend window list
                for apop in pops:
                    apop['chromosomes'][chromonr]['windows'].append( {'snpcount':0, 'maxval':0, 'avval':0 } )
            windowlist[windownr]['snpcount']+=1;
            windowlist[windownr]['maxval']=max(windowlist[windownr]['maxval'],statval);
            windowlist[windownr]['avval']+=statval;
            
            linecount+=1
            if (linecount%10000==0): print(linecount)
                    
        f.close()
    
    totalcount=0;
    failcount=0;
    for chromo in pop['chromosomes']:
        for win in chromo['windows']:
            totalcount+=win['snpcount']
            if win['snpcount']<10:
                failcount+=1;
    print("Total windows: "+str(totalcount))
    print("Failed windows: "+str(failcount))

#calculating averages
print("Calculating averages")
for pop in pops:
    for chromnr in range(1,chromocount+1):
        windowcount=min([len(pop['chromosomes'][chromnr]['windows']) for pop in pops])
        for windownr in range(0,windowcount):
            window=pop['chromosomes'][chromnr]['windows'][windownr]
            if (window['snpcount']>0):
                window['avval']=window['avval']/window['snpcount']
                


#filter out windows with too few snp
print("Filtering")
for pop in pops:
    for chromo in pop['chromosomes']:
        for window in chromo['windows']:
            if (window['snpcount']<minsnpcount):
                window['maxval']=-1


#calculate ranks
print("Calculating ranks")
for pop in pops:
    statlist=[]
    for chromo in pop['chromosomes']:
        for window in chromo['windows']:
            if (window[ranksource]>=0):
                statlist.append(window[ranksource])
    statlist.sort()
    for chromo in pop['chromosomes']:
        for window in chromo['windows']:
            rnk=1;
            if (window[ranksource]>=0):
                val=window[ranksource]
                i1=bisect.bisect_left(statlist,val)
                i2=bisect.bisect_right(statlist,val)-1
                if ((statlist[i1]!=val) or (statlist[i2]!=val)): raise Exception("Rank failed!")
                rnk=(len(statlist)-1-(i1+i2)/2.0)/(len(statlist)-1)
            window['maxrank']=rnk



#write results
print("Writing results")
f = open(basepath+"/XPEHH/_PV_XPEHHwindowed.txt",'w')


f.write('Chrom\tWinStart\tWinEnd')
for pop in pops:
    if exportcounts:
        f.write('\t'+pop['name']+'_SnpCount')
    if exportmaxval:
        f.write('\t'+pop['name']+'_MaxVal')
    f.write('\t'+pop['name']+'_MaxRank')
    if exportavval:
        f.write('\t'+pop['name']+'_AvVal')
f.write('\n')

for chromnr in range(1,chromocount+1):
    windowcount=min([len(pop['chromosomes'][chromnr]['windows']) for pop in pops])
    for windownr in range(0,windowcount):
        f.write(str(chromnr)+'\t'+str(windownr*windowsize)+'\t'+str((windownr+1)*windowsize))
        for pop in pops:
            thewin=pop['chromosomes'][chromnr]['windows'][windownr]
            if exportcounts:
                f.write('\t{0}'.format(thewin['snpcount']))
            if exportmaxval:
                f.write('\t{0:.5f}'.format(thewin['maxval']))
            f.write('\t{0:.5f}'.format(thewin['maxrank']))
            if exportavval:
                f.write('\t{0:.5f}'.format(thewin['avval']))
        f.write('\n')

f.close()

#write results per chromosome

for chromnr in range(1,chromocount+1):
    f = open(basepath+"/XPEHH/_PV_ChromoSplit/XPEHH_windowed_"+str(chromnr)+".txt",'w')
    f.write('Chrom\tWinStart\tWinEnd')
    for pop in pops:
        if exportcounts:
            f.write('\t'+pop['name']+'_SnpCount')
        if exportmaxval:
            f.write('\t'+pop['name']+'_MaxVal')
        f.write('\t'+pop['name']+'_MaxRank')
        if exportavval:
            f.write('\t'+pop['name']+'_AvVal')
    f.write('\n')
    windowcount=min([len(pop['chromosomes'][chromnr]['windows']) for pop in pops])
    for windownr in range(0,windowcount):
        f.write(str(chromnr)+'\t'+str(windownr*windowsize)+'\t'+str((windownr+1)*windowsize))
        for pop in pops:
            thewin=pop['chromosomes'][chromnr]['windows'][windownr]
            if exportcounts:
                f.write('\t{0}'.format(thewin['snpcount']))
            if exportmaxval:
                f.write('\t{0:.5f}'.format(thewin['maxval']))
            f.write('\t{0:.5f}'.format(thewin['maxrank']))
            if exportavval:
                f.write('\t{0:.5f}'.format(thewin['avval']))
        f.write('\n')
    f.close()


##export window information for liftover
#f = open(basepath+"/XPEHH/_PV_windows_build35.txt",'w')
#for chromnr in range(1,chromocount+1):
#    windowcount=min([len(pop['chromosomes'][chromnr]['windows']) for pop in pops])
#    for windownr in range(0,windowcount):
#        f.write("chr{0}\t{1}\t{2}\t{1}-{2}\n".format(chromnr,windownr*windowsize,(windownr+1)*windowsize))
#f.close()

print("Finished!")
