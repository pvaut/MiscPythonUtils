from TableUtils import VTTable
import sys

basedir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04'
outputdir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/Genotypes'

fl=open(basedir+'/public_samples.txt','r')
publicSamples=[line.rstrip() for line in fl]
fl.close()

print('Public samples: '+str(publicSamples))

#Process metadata
fli=open(basedir+'/_MetaData.txt','r')
flo=open(outputdir+'/_MetaData.txt','w')
for line in fli:
    token=line.split('=',1)[0]
    content=line.split('=',1)[1].rstrip()
    if token=='Samples':
        content=str(publicSamples)
    flo.write('{0}={1}\n'.format(token,content))
fli.close()
flo.close()
