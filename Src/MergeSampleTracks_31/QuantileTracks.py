import math
import os
import sys
import gzip
import DQXMathUtils

if len(sys.argv)<6:
    print('Usage: COMMAND sourcedir Component Chromosome First Last')
    sys.exit()

basedir=sys.argv[1]
compID=sys.argv[2]
chromID=sys.argv[3]
firstPos=int(sys.argv[4])
lastPos=int(sys.argv[5])

components = {}
components['Coverage']={
    'ID':'Coverage',
    'sourceName':'coverage_normed',
    'columnName':'dp_normed_median'
}
components['MapQuality']={
    'ID':'MapQuality',
    'sourceName':'mapq',
    'columnName':'rms_mapq'
}
component=components[compID]







class StatVectorCollector:
    def __init__(self,needQuantiles):
	self.needQuantiles=needQuantiles
	self.count=0
	self.n=[]
	self.mean=[]
	self.M2=[]
	self.minVal=[]
	self.maxVal=[]
	if self.needQuantiles:
	    self.dataList=[]

    def add(self,idx,val):
	if idx<0: raise Exception('Negative index')
	while self.count<=idx:
	    self.count+=1
	    self.n.append(0)
	    self.mean.append(0)
	    self.M2.append(0)
	    self.minVal.append(sys.float_info.max)
	    self.maxVal.append(-sys.float_info.max)
	    if self.needQuantiles:
		self.dataList.append([])
	self.n[idx]+= 1
	delta = val-self.mean[idx]
	self.mean[idx] += delta/self.n[idx]
	self.M2[idx] += delta*(val-self.mean[idx])
	self.minVal[idx] = min(self.minVal[idx],val)
	self.maxVal[idx] = max(self.maxVal[idx],val)
	if self.needQuantiles:
	    self.dataList[idx].append(val)

    def getCount(self):
	return self.count

    def getPresent(self,idx):
	if (idx<0) or (idx>=self.count): raise Exception('Index out of range')
	return self.n[idx]>0

    def getN(self,idx):
	if (idx<0) or (idx>=self.count): raise Exception('Index out of range')
	return self.n[idx]

    def getMean(self,idx):
	if (idx<0) or (idx>=self.count): raise Exception('Index out of range')
	if self.n[idx]<=0: raise Exception('No data present at point')
	return self.mean[idx]

    def getStDev(self,idx):
	if (idx<0) or (idx>=self.count): raise Exception('Index out of range')
	if self.n[idx]<=0: raise Exception('No data present at point')
	return math.sqrt(self.M2[idx]/self.n[idx])

    def getMin(self,idx):
	if (idx<0) or (idx>=self.count): raise Exception('Index out of range')
	if self.n[idx]<=0: raise Exception('No data present at point')
	return self.minVal[idx]

    def getMax(self,idx):
	if (idx<0) or (idx>=self.count): raise Exception('Index out of range')
	if self.n[idx]<=0: raise Exception('No data present at point')
	return self.maxVal[idx]

    def getQuantile(self,idx,fraction):
	if not(self.needQuantiles): raise Exception('Quantiles are not being calculated')
	if (fraction<0) or (fraction>1): raise Exception('Invalid quantile fraction')
	return DQXMathUtils.quantile(self.dataList[idx],fraction)

    def getMedian(self,idx):
	return self.getQuantile(idx,0.5)




#Define list of samples to be processed
allSampleList = [ sample for sample in os.listdir(basedir) ]
allSampleDict = { id:True for id in allSampleList }
fl=open('../IncludedSamples','r')
activeSampleList = [ line.rstrip() for line in fl ]
fl.close()
for sample in activeSampleList:
    if sample not in allSampleDict:
	raise Exception('Invalid sample '+sample)    
sampleList=activeSampleList
#sampleList=sampleList[0:50]#!!!warning: remove
print('SAMPLES: '+str(len(sampleList)))

tempFileName='TMP_{0}_{1}_{2}_{3}'.format(compID,chromID,firstPos,lastPos)

statVector = StatVectorCollector(True)
sampleNr = 0
for sampleid in sampleList:
    sampleNr += 1
    sourceFileName='{0}/{1}/{2}/{3}.txt.gz'.format(basedir,sampleid,chromID,component['sourceName'])
    print(str(sampleNr)+' '+sourceFileName)
    #fetch the column headers
    if os.path.isfile(sourceFileName):
        fl=gzip.open(sourceFileName,'r')
        columnHeaders=fl.readline().rstrip().split('\t')
        fl.close()
#       print(str(columnHeaders))
        columnHeaderDict={columnHeaders[i]:i for i in range(len(columnHeaders))}
        if columnHeaders[0]!='chrom':
            raise Exception('Invalid chrom column')
        if columnHeaders[1]!='pos':
            raise Exception('Invalid pos column')
        if component['columnName'] not in columnHeaderDict:
            raise Exception('Invalid data column '+component['columnName'])
        dataColNr=columnHeaderDict[component['columnName']]
        #fetch the data rows
        os.system('tabix {0} {1}:{2}-{3} > {4}'.format(sourceFileName,chromID,firstPos,lastPos,tempFileName))
        linenr=0
        fl=open(tempFileName,'r')
        for line in fl:
	    colValues=line.rstrip().split('\t')
	    if colValues[0]!=chromID: raise Exception('Invalid chromosome')
	    posit=int(colValues[1])
	    if (posit<firstPos) or (posit>lastPos): raise Exception('Invalid position')
	    value=float(colValues[dataColNr])
	    #print(str(posit)+' '+str(value))
	    statVector.add(posit-firstPos,value)
	    linenr+=1
        fl.close();
        os.remove(tempFileName)

#write out results
print('...saving results...')
outputDir='mergedQuantiles/{0}'.format(component['ID'])
if not os.path.exists(outputDir):
    os.makedirs(outputDir)
fl=open('{0}/{1}_{2}_{3}.txt'.format(outputDir,chromID,str(firstPos).zfill(8),str(lastPos).zfill(8)),'w')
fl.write('Position\t{0}Count\t{0}Q50\t{0}Q25\t{0}Q75\t{0}Q05\t{0}Q95\n'.format(compID))
for idx in range(statVector.getCount()):
    if statVector.getPresent(idx):
	fl.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(
	    idx+firstPos,
	    statVector.getN(idx),
	    statVector.getMedian(idx),
	    statVector.getQuantile(idx,0.25),
	    statVector.getQuantile(idx,0.75),
	    statVector.getQuantile(idx,0.05),
	    statVector.getQuantile(idx,0.95)
	))
fl.close()

sys.exit()

