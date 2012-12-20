import math
import bisect
import Utils

basepath="C:/Data/Articles/PositiveSelection/DataSaturn"



windowsize=200000
statthreshold=2.0
minsnpcount=11       #!! should be 11 conform the paper
chromocount=22

exportcounts=False
exportfrac=False
exportmaxval=False

pops=[]


#build start information about what populations to process
apop={}

#pops.append({'name':'Ghana', 'files':['Ghana_Untransmitted_ihs_standardized.txt']})
#pops.append({'name':'Gambia', 'files':['Gambia_all_Untransmitted_ihs_standardized.txt']})

#pops.append({'name':'YRI', 'files':['YRI_650Y_matched_ihs_standardized.txt']})
#pops.append({'name':'Malawi', 'files':['Malawi_Untransmitted_ihs_standardized.txt']})
#pops.append({'name':'Mandinka', 'files':['Mandinka_Untransmitted_ihs_standardized.txt']})
#pops.append({'name':'Wolof', 'files':['Wolof_Untransmitted_ihs_standardized.txt']})
#pops.append({'name':'Fula', 'files':['Fula_Untransmitted_ihs_standardized.txt']})
pops.append({'name':'Jola', 'files':['Jola_Untransmitted_ihs_standardized.txt']})
#pops.append({'name':'Akan', 'files':['Akan_Untransmitted_ihs_standardized.txt']})
#pops.append({'name':'Northerner', 'files':['Northerner_Untransmitted_ihs_standardized.txt']})

#initialise chromosomes & window accumulators
for pop in pops:
    pop['chromosomes']=[]
    for i in range(0,chromocount+1):
        achromo={}
        achromo['windows']=[]
        pop['chromosomes'].append(achromo)


#main loop over all populations
for pop in pops:
        
    #scan all files associated with this population
    for file in pop['files']:
        f = open(basepath+"/IHS/"+file)
        linecount=0;
        for line in f:
            line=line.rstrip('\r\n')
            cells=line.split("\t")
            chromonr=int(cells[1])
            posit=int(cells[2])
            statval=float(cells[9])
            
            windownr=int(posit/windowsize)
            if (posit<windownr*windowsize) or (posit>(windownr+1)*windowsize):
                raise Exception('This is wrong!')
            windowlist=pop['chromosomes'][chromonr]['windows']
            while len(windowlist)<=windownr:#extend window list
                for apop in pops:
                    apop['chromosomes'][chromonr]['windows'].append( {'snpcount':0, 'snplargecount':0, 'maxval':0 } )
            windowlist[windownr]['snpcount']+=1;
            windowlist[windownr]['maxval']=max(windowlist[windownr]['maxval'],statval);
            if (statval>statthreshold): windowlist[windownr]['snplargecount']+=1;
            
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
    

#filter out windows with too few snp
print("Filtering")
for pop in pops:
    for chromo in pop['chromosomes']:
        for window in chromo['windows']:
            if (window['snpcount']<minsnpcount):
                window['snplargecount']=-1

#calculate fraction above threshold
print("Calculating fractions")
for pop in pops:
    for chromo in pop['chromosomes']:
        for window in chromo['windows']:
            frac=0
            if (window['snplargecount']>0):
                frac=window['snplargecount']/window['snpcount']
            if (window['snplargecount']<0):
                frac=-1
            window['snplargefraction']=frac

#calculate ranks
print("Calculating ranks")
for pop in pops:
    statlist=[]
    for chromo in pop['chromosomes']:
        for window in chromo['windows']:
            if (window['snplargefraction']>=0):
                statlist.append(window['snplargefraction'])
                statlist.sort()
    for chromo in pop['chromosomes']:
        for window in chromo['windows']:
            rnk=1;
            if (window['snplargefraction']>=0):
                val=window['snplargefraction']
                i1=bisect.bisect_left(statlist,val)
                i2=bisect.bisect_right(statlist,val)-1
                rnk=(len(statlist)-1-(i1+i2)/2.0)/(len(statlist)-1)
            window['snpstatrank']=rnk



#write results
print("Writing results")
f = open(basepath+"/IHS/_PV_IHSwindowed.txt",'w')


f.write('Chrom\tWinStart\tWinEnd')
for pop in pops:
    if exportcounts:
        f.write('\t'+pop['name']+'_SnpCount')
        f.write('\t'+pop['name']+'_SnpLargeCount')
    if exportfrac:
        f.write('\t'+pop['name']+'_SnpLargeFraction')
    f.write('\t'+pop['name']+'_SnpLargeFractionRank')
    if exportmaxval:
        f.write('\t'+pop['name']+'_MaxVal')
f.write('\n')

for chromnr in range(1,chromocount+1):
    windowcount=min([len(pop['chromosomes'][chromnr]['windows']) for pop in pops])
    for windownr in range(0,windowcount):
        f.write(str(chromnr)+'\t'+str(windownr*windowsize)+'\t'+str((windownr+1)*windowsize))
        for pop in pops:
            thewin=pop['chromosomes'][chromnr]['windows'][windownr]
            if exportcounts:
                f.write('\t{0}\t{1}'.format(thewin['snpcount'],thewin['snplargecount']))
            if exportfrac:
                f.write('\t{0:.5f}'.format(thewin['snplargefraction']))
            f.write('\t{0:.5f}'.format(thewin['snpstatrank']))
            if exportmaxval:
                f.write('\t{0:.5f}'.format(thewin['maxval']))
        f.write('\n')

f.close()
print("Finished!")
