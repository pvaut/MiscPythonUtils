sourcedir='C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData'


f=open(sourcedir+'/metadata-2.0.2.txt','r')
sampleUse={}
sampleCountry={}
f.readline()
for line in f:
    cells=line.split('\t')
    sampleid=cells[1]
    country=cells[3]
    skip=(cells[9]=='TRUE')
    sampleUse[sampleid]=not(skip)
    if not(skip):
        sampleCountry[sampleid]=country
    pass
    
f.close()
print('finished')

f=open(sourcedir+'/GenotypesFreq.tab','r')
sampleOffset=4
snpCol=3

ofile=open('C:/Data/Genomes/PlasmodiumFalciparum/Release_21/SnpCountryFreqs.txt','w')

line=f.readline().rstrip()
print(line)
sampleCols=line.split('\t')[sampleOffset:]
print(str(sampleCols))


linenr=0
for line in f:
    cells=line.rstrip().split('\t')
    snpid=cells[snpCol]
    freqsStr=cells[sampleOffset:]
    
    countryTotFreq={}
    countryTotCount={}
    for colnr in range(len(sampleCols)):
        if sampleUse[sampleCols[colnr]]:
            country=sampleCountry[sampleCols[colnr]]
            if freqsStr[colnr]!='-':
                if not(country in countryTotCount):
                    countryTotCount[country]=0
                    countryTotFreq[country]=0
                countryTotFreq[country]+=float(freqsStr[colnr])
                countryTotCount[country]+=1
    for country in countryTotCount:
        ofile.write(snpid+'\t0\t'+country+'\t'+str(countryTotFreq[country])+'\t'+str(countryTotCount[country])+'\n')
    
    linenr+=1
    if linenr%200==0: print(linenr)
    
    #if linenr>20: break
f.close()
ofile.close()