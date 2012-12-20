

sourcefilename='C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData/genes.dat'
outputfilename='C:/Data/Genomes/PlasmodiumFalciparum/Release_21/annot.txt'
f=open(sourcefilename,'r')
f2=open(outputfilename,'w')

for line in f:
    line=line.rstrip()
    tokens=line.split('\t')
    geneid=tokens[0]
    names=tokens[1]
    description=tokens[2]
    chromid=tokens[3]
    strand=tokens[4]
    exonstart=[]
    exonstop=[]
    for i in range(5,len(tokens)):
        if len(tokens[i])>0:
            exonlimits=tokens[i].split('-')
            exonstart.append(int(exonlimits[0]))
            exonstop.append(int(exonlimits[1]))
    featurestart=min(exonstart)
    featurestop=max(exonstop)
    firstname=names.split(';')[0]
    f2.write('{0}\t{1}\t{2}\t{3}\t\tgene\t{4}\t{5}\t{6}\t{7}'.format(
        chromid,
        featurestart,
        featurestop,
        geneid,
        firstname,
        names,
        description,
        strand
        ))
    f2.write('\n')
    for exonnr in range(len(exonstart)):
        f2.write('{0}\t{1}\t{2}\t{3}\t{4}\texon\t\t\t\t'.format(
            chromid,
            exonstart[exonnr],
            exonstop[exonnr],
            geneid+'_exon_'+str(exonnr+1),
            geneid
            ))
        f2.write('\n')
        

f.close()
f2.close()
print('finished')