#from TableUtils import VTTable
import sys
import hashlib
import os
import shutil

def hash(str):
    return hashlib.md5('salt'+str+'pepper'+str).hexdigest()


if len(sys.argv)<2:
    print('Usage: COMMAND OutputDir')
    sys.exit()

#basedir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04'
#outputdir = 'C:/Data/Genomes/PlasmodiumFalciparum/Release_21/OriginalData_04/Output/Genotypes'

basedir='.'
outputdir=sys.argv[1]

fl=open(basedir+'/public_samples.txt','r')
publicSamples=[line.rstrip() for line in fl]
publicSamplesMap={id:True for id in publicSamples}
fl.close()

print('Public samples: '+str(publicSamples))

#Process metadata
fli=open(basedir+'/_MetaData.txt','r')
flo=open(outputdir+'/_MetaData.txt','w')
for line in fli:
    token=line.split('=',1)[0]
    content=line.split('=',1)[1].rstrip()
    if token=='Samples':
        content=str([hash(smp) for smp in publicSamples])
    flo.write('{0}={1}\n'.format(token,content))
fli.close()
flo.close()

fileCount=0
for fname in os.listdir(basedir):
#    if fileCount>5: break
    chromid=fname.split('_',1)[0]
    st=fname.split('_',1)[1]
    sampleid=st.split('.',1)[0]
    ext=st.split('.',1)[1]
    if sampleid in publicSamplesMap:
        fileCount += 1
        outputFileName = chromid+'_'+hash(sampleid)+'.'+ext
        print(fname+' '+chromid+' '+sampleid+' '+ext+'  ->  '+outputFileName)
        shutil.copyfile(basedir+'/'+fname,outputdir+'/'+outputFileName)


print('Files: '+str(fileCount))
