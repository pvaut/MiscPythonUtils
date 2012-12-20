

sourcedir='C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData'
freqtypes=['nraf','maf','daf']
regionoffset=4
regioncount=6

outputfilename='C:/Data/Genomes/PlasmodiumFalciparum/Release_21/snpdata.txt'


f0=open(sourcedir+'/SnpInfo.tab','r')
filesFreq=[open(sourcedir+'/AlleleFreq-{0}.tab'.format(x),'r') for x in freqtypes]
f2=open(outputfilename,'w')

linenr=0
for line0 in f0:
    line0=line0.rstrip()
    linesFreq=[file.readline().rstrip() for file in filesFreq]
    
    tokens=line0.split('\t')
    snpid=tokens[3]
    
    #convert chromosome id to number
    tokens[1]=tokens[1][3:]
    
    for i in range(len(tokens)):
        if i>0:
            f2.write('\t')
        f2.write(tokens[i])
    
    for freqline in linesFreq:
        tokens=freqline.split('\t')
        if tokens[3]!=snpid:
            raise "Inconsistent snp id"
        for i in range(regionoffset,regionoffset+regioncount):
            if tokens[i]=='-':
                tokens[i]='\\N'
            f2.write('\t'+tokens[i])
            
    #calculate Fst from nraf
    FST=0
    if linenr>0:
        tokens=linesFreq[0].split('\t')
        popfreqs=[]
        for i in range(regionoffset,regionoffset+regioncount):
            popfreqs.append(float(tokens[i]))
        popfreqavg=sum(popfreqs)/len(popfreqs)
        Havg=sum([p*(1-p) for p in popfreqs])/len(popfreqs)
        Ht=popfreqavg*(1-popfreqavg)
        if Ht>0:
            FST=(Ht-Havg)/Ht
        pass
    f2.write('\t'+str(FST))
    
    f2.write('\n')
    linenr+=1
    if linenr%5000==0:
        print(str(linenr))
    
    
    #if linenr>100: break;

f0.close()
f2.close()

print('finished')