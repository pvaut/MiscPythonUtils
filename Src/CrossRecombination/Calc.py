from TableUtils import VTTable
import sys
import numpy
import DQXMathUtils
import simplejson

import numpy as np
import matplotlib.pyplot as plt


import matplotlib.pyplot as plt

chromosomeInfo = [
            { 'id': 'Pf3D7_01_v3', 'len': 0.640851E6 },
            { 'id': 'Pf3D7_02_v3', 'len': 0.947102E6 },
            { 'id': 'Pf3D7_03_v3', 'len': 1.067971E6 },
            { 'id': 'Pf3D7_04_v3', 'len': 1.200490E6 },
            { 'id': 'Pf3D7_05_v3', 'len': 1.343557E6 },
            { 'id': 'Pf3D7_06_v3', 'len': 1.418242E6 },
            { 'id': 'Pf3D7_07_v3', 'len': 1.445207E6 },
            { 'id': 'Pf3D7_08_v3', 'len': 1.472805E6 },
            { 'id': 'Pf3D7_09_v3', 'len': 1.541735E6 },
            { 'id': 'Pf3D7_10_v3', 'len': 1.687656E6 },
            { 'id': 'Pf3D7_11_v3', 'len': 2.038340E6 },
            { 'id': 'Pf3D7_12_v3', 'len': 2.271494E6 },
            { 'id': 'Pf3D7_13_v3', 'len': 2.925236E6 },
            { 'id': 'Pf3D7_14_v3', 'len': 3.291936E6 }
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

def SimulateEvents():
    chromoids = []
    posits = []

    for chromoInfo in chromosomeInfo:
        chromoId=chromoInfo['id']
        avcount=chromoInfo['eventcount']
        simcount = numpy.random.poisson(avcount)
        #print('avcount = {0} simcount = {1}'.format(avcount,simcount))
        chromoposits = []
        for simnr in range(simcount):
            chromoposits.append(int(numpy.random.rand()*chromoInfo['len']))
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


def SimulateStats(winSize):
    maxcount = 20
    countsList =[[] for i in range(maxcount)]
    for simnr in range(500):#!!! should be at least 10000
        print('Simulation {0}'.format(simnr))
        simevents = SimulateEvents()
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


winSizeList = [500,1000,2000,5000,10000,20000,50000]


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
fig.set_size_inches(10,30)


for winSize in winSizeList:
    print('\n\n\nWINDOW SIZE {0}'.format(winSize))
    plotnr += 1
    plt.subplot(len(winSizeList),1,plotnr)

    rs = CalcIt(events,winSize)
    print('SizecountsCumul: '+str(rs['sizecountscumul']))


    sizecountscumul = rs['sizecountscumul']
    plt.semilogy(sizecountscumul)
    plt.semilogy(sizecountscumul,'wo')



    if True:
        simpts = [ simuldata[str(winSize)][nr]['average'] for nr in range(len(sizecountscumul)) ]
        print(str(simpts))
        plt.semilogy(simpts,'r-')
        plt.semilogy(simpts,'wo')

        simpts = [ simuldata[str(winSize)][nr]['q99'] for nr in range(len(sizecountscumul)) ]
        print(str(simpts))
        plt.semilogy(simpts,'r--')
        plt.semilogy(simpts,'wo')

        simpts = [ simuldata[str(winSize)][nr]['q999'] for nr in range(len(sizecountscumul)) ]
        print(str(simpts))
        plt.semilogy(simpts,'r:')
        plt.semilogy(simpts,'wo')

        plt.xlim(0,12)

#plt.ylabel('some numbers')
plt.show()

sys.exit()
