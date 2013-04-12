import os
import sys

fl=open('ChromoLengths.txt','r')
chromoLengths= { line.split('\t')[0] : int(line.rstrip().split('\t')[1]) for line in fl }
fl.close()

#chromoLengths={'MAL11':2100000}

print(str(chromoLengths))
#sys.exit()

properties=['Coverage','MapQuality']
#properties=['MapQuality']

blockSize=10000

missing=[]

for prop in properties:
    for chromID in chromoLengths:
	flo=open('results/{0}/{1}.txt'.format(prop,chromID),'w')
	offset=0
	firstBlock=True
	ct = 0
	while offset<chromoLengths[chromID]:
	    fileName='jobs/mergedQuantiles/{0}/{1}_{2}_{3}.txt'.format(prop,chromID,str(offset+1).zfill(8),str(offset+blockSize).zfill(8))
	    if os.path.isfile(fileName):
		print(fileName)
		fli=open(fileName,'r')
		firstLine=True
		for line in fli:
		    if firstBlock or not(firstLine):
			flo.write(line)
		    firstLine=False
		    ct += 1
		fli.close()
	    else:
		print("*** MISSING: "+fileName)
		missing.append(fileName)
	    offset+=blockSize
	    firstBlock=False
	print('finishing output file')
	flo.close()

print('============================')
print('Missing files: '+str(missing))
