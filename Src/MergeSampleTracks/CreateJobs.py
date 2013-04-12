import os



fl=open('ChromoLengths.txt','r')
chromoLengths= { line.split('\t')[0] : int(line.rstrip().split('\t')[1]) for line in fl }
fl.close()
print(str(chromoLengths))

#properties=['Coverage']
properties=['Coverage','MapQuality']

blockSize=10000

sourceDir='/data/galton2/plasmodium/PfPopGenWeb/data/stats'

if not(os.path.exists('jobs')):
    os.makedirs('jobs')

fll=open('jobs/launcher.sh','w')
fll.write('#!/bin/bash\n')

for prop in properties:
    for chromID in chromoLengths:
	offset=0
	while offset<chromoLengths[chromID]:
	    jobID='MergePfPopgenTracks_{0}_{1}_{2}'.format(prop,chromID,offset+1)
	    cmd='python ../QuantileTracks.py {0} {1} {2} {3} {4}'.format(sourceDir,prop,chromID,offset+1,offset+blockSize)
	    fl=open('jobs/{0}.sh'.format(jobID),'w')
	    fl.write('#!/bin/bash\n')
	    fl.write(cmd+'\n')	
	    fl.close()
	    fll.write('qsub -cwd -V -N {0} {1}.sh\n'.format(jobID,jobID))
	    offset+=blockSize

fll.close()
os.system('chmod +x jobs/launcher.sh')
