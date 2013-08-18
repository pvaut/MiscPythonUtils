from TableUtils import VTTable
import sys
import numpy
import DQXMathUtils
import simplejson

import numpy as np
import matplotlib.pyplot as plt


import matplotlib.pyplot as plt

#SampleCount = 124
SampleCount = 37

chromosomeInfo = [
            { 'id': 'Pf3D7_01_v3', 'len': int(0.640851E6) },
            { 'id': 'Pf3D7_02_v3', 'len': int(0.947102E6) },
            { 'id': 'Pf3D7_03_v3', 'len': int(1.067971E6) },
            { 'id': 'Pf3D7_04_v3', 'len': int(1.200490E6) },
            { 'id': 'Pf3D7_05_v3', 'len': int(1.343557E6) },
            { 'id': 'Pf3D7_06_v3', 'len': int(1.418242E6) },
            { 'id': 'Pf3D7_07_v3', 'len': int(1.445207E6) },
            { 'id': 'Pf3D7_08_v3', 'len': int(1.472805E6) },
            { 'id': 'Pf3D7_09_v3', 'len': int(1.541735E6) },
            { 'id': 'Pf3D7_10_v3', 'len': int(1.687656E6) },
            { 'id': 'Pf3D7_11_v3', 'len': int(2.038340E6) },
            { 'id': 'Pf3D7_12_v3', 'len': int(2.271494E6) },
            { 'id': 'Pf3D7_13_v3', 'len': int(2.925236E6) },
            { 'id': 'Pf3D7_14_v3', 'len': int(3.291936E6) }
            ]

chromosomes = [info['id'] for info in chromosomeInfo]
#print(str(Chromosomes))


tb=VTTable.VTTable()
tb.allColumnsText=True
tb.LoadFile('posits.txt')
tb.ConvertColToValue('pos_mid')
tb.RenameCol('pos_mid','pos')

tb.DropCol('pos_min')
tb.DropCol('pos_max')
tb.DropCol('pos_range')
tb.DropCol('sample')
tb.DropCol('cross')

tbcol_chrom=tb.GetColNr('chrom')
tbcol_pos=tb.GetColNr('pos')

tb.PrintRows(0,6);


events={
    'chromoids' : [tb.GetValue(rownr,tbcol_chrom) for rownr in tb.GetRowNrRange()],
    'posits' : [tb.GetValue(rownr,tbcol_pos) for rownr in tb.GetRowNrRange()]
}
event_chromoids=events['chromoids']
event_posits=events['posits']

#Calculate total number of events per chromosome
for chromoInfo in chromosomeInfo:
    chromoId=chromoInfo['id']
    chromoLen=chromoInfo['len']
    cnt = 0
    for nr in range(len(event_chromoids)):
        if event_chromoids[nr] == chromoId:
            cnt += 1
    chromoInfo['eventcount'] = cnt
    chromoInfo['eventrate'] = cnt/chromoInfo['len']
    print('Chromosome {0}: {1} events ( rate {2})'.format(chromoId,cnt,chromoInfo['eventrate']))
print('Total events: {0}'.format(len(event_posits)))

#print(str(events['chromoids']))

def FindClosest(lst,pos):
    #print(str(lst))
    i1 = 0
    i2 = len(lst)-1
    while i2 > i1+1:
        i = int((i1+i2)/2)
        #print('{0} {1} | {2} {3} | {4}'.format(i1,i2,lst[i1],lst[i2],pos))
        if lst[i] > pos:
            i2=i
        else:
            i1=i
    #print('{0} {1}'.format(pos,lst[i]))
    #sys.exit()
    if (pos<lst[i1]) or (pos>lst[i2]) or (i2!=i1+1):
        raise Exception('Impossible!')
    return int((lst[i1]+lst[i2])/2)

def SimulateEvents(snpposits):
    chromoids = []
    posits = []

    RandomPositions = False

    for chromoInfo in chromosomeInfo:
        chromoId=chromoInfo['id']
        avcount=chromoInfo['eventcount']
        simcount = numpy.random.poisson(avcount)
        snppositsonchromo = snpposits[chromoId]

        if RandomPositions:
            cntt = int(len(snppositsonchromo))
            snppositsonchromo = []
            for i1 in range(cntt):
                snppositsonchromo.append(int(numpy.random.rand()*chromoInfo['len']))

        chromoposits = []
        for SampleNr in range(SampleCount):
            simcount = numpy.random.poisson(avcount*1.0/SampleCount)

            simnr=0
            eventposits=[]
            while simnr < simcount:
                if RandomPositions:
                    randomsnpnr = int(numpy.random.rand()*len(snppositsonchromo))
                    randomposit = snppositsonchromo[randomsnpnr]
                else:
                    randomposit = int(numpy.random.rand()*chromoInfo['len'])
                    if (randomposit>=snppositsonchromo[1]) and (randomposit<=snppositsonchromo[len(snppositsonchromo)-2]):
                        randomposit=FindClosest(snppositsonchromo,randomposit)
                    else:
                        randomposit = -1
                if randomposit >= 0:
                    isok=True
                    for otherevent in eventposits:
                        if abs(otherevent-randomposit)<25000:
                            isok=False
                    if isok:
                        eventposits.append(randomposit)
                        chromoposits.append(randomposit)
                        simnr += 1

        chromoposits = sorted(chromoposits)
        #print(str(chromoposits))
        for posit in chromoposits:
            chromoids.append(chromoId)
            posits.append(posit)

    return {
        'chromoids' : chromoids,
        'posits' : posits
    }



def CalcIt(events, winSize):

    event_chromoids=events['chromoids']
    event_posits=events['posits']
    eventcount=len(event_posits)

    #This will contain the number of windows having a given number of events
    #Array argument = number of events
    #Array value = number of windows
    sizeCounts=[]

    for chromoInfo in chromosomeInfo:
        chromoId=chromoInfo['id']
        chromoLen=chromoInfo['len']
        #Obtain positions for this chromosome
        posits=[]
        for nr in range(eventcount):
            if event_chromoids[nr] == chromoId:
                posits.append(event_posits[nr])
        posits=sorted(posits)
        winStart=0
        positnr=0
        while winStart<chromoLen:
            cnt = 0
            while (positnr<len(posits)) and (posits[positnr]<winStart):
                positnr += 1
            positnr2 = positnr
            while (positnr2<len(posits)) and (posits[positnr2]<winStart+winSize):
                if (posits[positnr2]>=winStart) and (posits[positnr2]<winStart+winSize):
                    cnt += 1
                positnr2 += 1
            while len(sizeCounts)<=cnt:
                sizeCounts.append(0)
            sizeCounts[cnt] += 1
            winStart+=winSize/2
    sizeCountsCumul =[]
    for size in range(len(sizeCounts)):
        ct=0
        size2=size
        while size2<len(sizeCounts):
            ct += sizeCounts[size2]
            size2 += 1
        sizeCountsCumul.append(ct)
    return {
        'sizecounts' : sizeCounts,
        'sizecountscumul' : sizeCountsCumul
    }


def LoadSnpPositions():
    print('start loading snps')
    positsperchromo={}
    files = ['snpposits_3d7_hb3.txt', 'snpposits_7g8_gb4.txt', 'snpposits_hb3_dd2.txt', 'snpposits_3d7_hb3_cortex.txt', 'snpposits_7g8_gb4_cortex.txt', 'snpposits_hb3_dd2_cortex.txt']
    for file in files:
        snps=VTTable.VTTable()
        snps.allColumnsText=True
        snps.LoadFile(file)
        for rownr in snps.GetRowNrRange():
            st=snps.GetValue(rownr,0)
            chromid = st.split(':')[0]
            pos = int(st.split(':')[1])
            if chromid not in positsperchromo:
                positsperchromo[chromid]=[]
            positsperchromo[chromid].append(pos)
    print('snps loaded')
    for chromoid in positsperchromo:
        lst = sorted(positsperchromo[chromoid])
        nr=0
        while nr<len(lst)-1:
            if lst[nr] == lst[nr+1]:
                del lst[nr]
            else:
                nr += 1
        positsperchromo[chromoid] = lst
        #print('chromo: {0} snpcount {1}'.format(chromoid,len(positsperchromo[chromoid])))
    #sys.exit()
    return positsperchromo

def SimulateStats(winSize):
    snpposits = LoadSnpPositions()
    maxcount = 200
    countsList =[[] for i in range(maxcount)]
    for simnr in range(10000):#!!! should be at least 10000
        print('Simulation {0}'.format(simnr))
        simevents = SimulateEvents(snpposits)
        #print('Simulated total events: {0}'.format(len(simevents['posits'])))
        rs = CalcIt(simevents,winSize)
        print(str(rs['sizecountscumul']))
        sizecountscumul = rs['sizecountscumul']
        for nr in range(maxcount):
            if nr<len(sizecountscumul):
                countsList[nr].append(sizecountscumul[nr])
            else:
                countsList[nr].append(0)
    rs = []
    for nr in range(len(countsList)):
        vals={}
        samples = sorted(countsList[nr])
        vals['average'] = sum(samples)*1.0/len(samples)
        vals['median'] = DQXMathUtils.quantile(samples,0.5,7,True)
        vals['q95'] = DQXMathUtils.quantile(samples,0.95,7,True)
        vals['q99'] = DQXMathUtils.quantile(samples,0.99,7,True)
        vals['q999'] = DQXMathUtils.quantile(samples,0.999,7,True)
        rs.append(vals)
    return rs


winSizeList = [2000,5000,10000,20000]


# Generate or load the simulated data
if False:
    simuldata={}
    for winSize in winSizeList:
        simuldata[str(winSize)] = SimulateStats(winSize)
    fp=open('simuldata','w')
    simplejson.dump(simuldata,fp)
    fp.close()
else:
    fp=open('simuldata','r')
    simuldata = simplejson.load(fp)
    fp.close()

print(str(simuldata))

plotnr = 0;
fig = plt.figure(1)
fig.set_size_inches(15,30)


for winSize in winSizeList:
    print('\n\n\nWINDOW SIZE {0}'.format(winSize))
    plotnr += 1
    plt.subplot(len(winSizeList),1,plotnr)
    plt.title('Window size {0}'.format(winSize))

    rs = CalcIt(events,winSize)
    sizecountscumul = rs['sizecountscumul']
    print('SizecountsCumul: '+str(sizecountscumul))

    simpts_av = [ simuldata[str(winSize)][nr]['average'] for nr in range(len(sizecountscumul)) ]
    simpts_q99 = [ simuldata[str(winSize)][nr]['q99'] for nr in range(len(sizecountscumul)) ]
    simpts_q999 = [ simuldata[str(winSize)][nr]['q999'] for nr in range(len(sizecountscumul)) ]

    plt.semilogy(sizecountscumul)
    plt.semilogy(sizecountscumul,'bo')

    for idx in range(len(sizecountscumul)):
        plt.annotate(
            '{0}, {1}, {2}'.format(sizecountscumul[idx],simpts_av[idx],simpts_q99[idx]),
            xy = (idx, sizecountscumul[idx]),
            xytext = (15, 15),
            textcoords = 'offset points',
            size=7,
#            ha = 'right', va = 'bottom',
#            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
        )




    plt.semilogy(simpts_av,'r-')
    plt.semilogy(simpts_av,'wo')
    plt.semilogy(simpts_q99,'r--')
    plt.semilogy(simpts_q99,'wo')
    plt.semilogy(simpts_q999,'r:')
    plt.semilogy(simpts_q999,'wo')

    plt.xlim(0,12)

#plt.ylabel('some numbers')
plt.savefig('plots/plot1.png')
plt.show()

sys.exit()
