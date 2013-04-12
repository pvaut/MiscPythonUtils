import math
import os
import sys
import gzip

if len(sys.argv)<2:
    print('Usage: COMMAND sourcedir [Component] [Chromosome]')
    sys.exit()

basedir=sys.argv[1]

#Define components to be processed
components=[]
components.append({
    'ID':'Coverage',
    'sourceName':'coverage_normed',
    'columnName':'dp_normed_median'
})
components.append({
    'ID':'MapQuality',
    'sourceName':'mapq',
    'columnName':'rms_mapq'
})
if len(sys.argv)>2:
    compID=sys.argv[2]
    components = [ comp for comp in components if comp['ID']==compID ]
    if len(components)!=1:
	raise Exception('Invalid component '+compID)
print('COMPONENTS: '+str(components))

maxPosCount=-1
#maxPosCount=5#!!!warning: should be -1
#maxPosCount=5000#!!!warning: should be -1
#maxPosCount=100000#!!!warning: should be -1


#Define list of samples to be processed
allSampleList = [ sample for sample in os.listdir(basedir) ]
allSampleDict = { id:True for id in allSampleList }
fl=open('IncludedSamples','r')
activeSampleList = [ line.rstrip() for line in fl ]
fl.close()
for sample in activeSampleList:
    if sample not in allSampleDict:
	raise Exception('Invalid sample '+sample)    
sampleList=activeSampleList
#sampleList=sampleList[0:10]#!!!warning: remove
print('SAMPLES: '+str(len(sampleList)))


#Define list of chromosomes to be processed
chromoList=['MAL'+str(i) for i in range(1,15)]
if len(sys.argv)>3:
    chromoList=[sys.argv[3]]
print('CHROMOSOMES: '+str(chromoList))





class StatVectorCollector:
    def __init__(self):
	self.count=0
	self.n=[]
	self.mean=[]
	self.M2=[]
	self.minVal=[]
	self.maxVal=[]

    def add(self,idx,val):
	if idx<0: raise Exception('Negative index')
	while self.count<=idx:
	    self.count+=1
	    self.n.append(0)
	    self.mean.append(0)
	    self.M2.append(0)
	    self.minVal.append(sys.float_info.max)
	    self.maxVal.append(-sys.float_info.max)
	self.n[idx]+= 1
	delta = val-self.mean[idx]
	self.mean[idx] += delta/self.n[idx]
	self.M2[idx] += delta*(val-self.mean[idx])
	self.minVal[idx] = min(self.minVal[idx],val)
	self.maxVal[idx] = max(self.maxVal[idx],val)

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

totItemCount=len(components)*len(chromoList)*len(sampleList)
itemNr=0

for component in components:

    for chromo in chromoList:
	statVector=StatVectorCollector()
        for sample in sampleList:
	    itemNr += 1
            fileName=basedir+'/'+sample+'/'+chromo+'/'+component['sourceName']+'.txt.gz'
            print('Processing '+str(itemNr)+'/'+str(totItemCount)+'   '+component['sourceName']+' '+chromo+' '+sample+'    '+fileName)
            if not(os.path.exists(fileName)):
                print('Missing: '+fileName)
            else:
                fl=gzip.open(fileName,'r')
                columnHeaders=fl.readline().rstrip().split('\t')
#		print(str(columnHeaders))
		columnHeaderDict={columnHeaders[i]:i for i in range(len(columnHeaders))}
		if columnHeaders[0]!='chrom':
		    raise Exception('Invalid chrom column')
		if columnHeaders[1]!='pos':
		    raise Exception('Invalid pos column')
		if component['columnName'] not in columnHeaderDict:
		    raise Exception('Invalid data column '+component['columnName'])
		dataColNr=columnHeaderDict[component['columnName']]
		linenr=0
		for line in fl:
		    colValues=line.rstrip().split('\t')
#		    if linenr<10:
#			print(str(colValues))
		    if colValues[0]!=chromo: raise Exception('Invalid chromosome')
		    posit=int(colValues[1])
		    value=float(colValues[dataColNr])
		    statVector.add(posit,value)
		    linenr+=1
		    if linenr%100000==0: print('    '+str(linenr))
		    if (maxPosCount>0) and (linenr>maxPosCount): break
		fl.close()

	#write out results
	print('...saving results...')
	outputDir='merged2/{0}'.format(component['ID'])
	if not os.path.exists(outputDir):
	    os.makedirs(outputDir)
	fl=open('{0}/{1}.txt'.format(outputDir,chromo),'w')
	fl.write('Position\t{0}Count\t{0}Mean\t{0}StdevLower\t{0}StdevUpper\t{0}Min\t{0}Max\n'.format(component['ID']))
	for idx in range(statVector.getCount()):
	    if statVector.getPresent(idx):
		mean=statVector.getMean(idx)
		stdev=statVector.getStDev(idx)
		mn=statVector.getMin(idx)
		mx=statVector.getMax(idx)
		fl.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n'.format(
		    idx,
		    statVector.getN(idx),
		    mean,
		    max(mn,mean-stdev),
		    min(mx,mean+stdev),
		    mn,
		    mx
		))
	fl.close()
print('finished')
sys.exit()



fileName=basedir+'/'+sampleList[0]+'/'+chromoList[0]+'/'+sourceName+'.txt.gz'
fl=gzip.open(fileName)
linenr=0
for line in fl:
    if linenr%10000==0: print('line '+str(linenr))
    if linenr<10:
        print(fl.readline().rstrip())
    linenr+=1
fl.close()
