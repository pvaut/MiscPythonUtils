import math
#import sys
import Utils


basepath="C:/Data/Articles/PositiveSelection/DataSaturn"

pops=[]

pops.append({'name':'YRI'})
pops.append({'name':'Malawi'})
pops.append({'name':'Mandinka'})
pops.append({'name':'Wolof'})
pops.append({'name':'Fula'})
pops.append({'name':'Jola'})
pops.append({'name':'Akan'})
pops.append({'name':'Northerner'})



def DrawChart(dispchromosome, dispcenterposit, disphalfwidth=4.0E6):
    #main loop over all populations
    for pop in pops:
    
        f = open('{0}/XPEHH/CEU_Reference/CEU_{1}_650Y_XP_EHH_standardized.txt'.format(basepath, pop['name']))
    
        f2 = open('{0}/ChartData/XPEHH/{1}.txt'.format(basepath, pop['name']), 'w')
        f2.write('Posit\tStatVal\n') 
        linecount = 0;
        for line in f:
            line = line.rstrip('\r\n')
            cells = line.split("\t")
            chromonr = int(cells[0])
            posit = int(cells[2])
            statval = float(cells[8])
        
            if (chromonr == dispchromosome):
                if (math.fabs(posit - dispcenterposit) <= disphalfwidth):
                    f2.write('{0}\t{1}\n'.format(posit, statval)) 
            
            linecount += 1
            if (linecount % 10000 == 0): print('{0}, {1}'.format(pop['name'], linecount))
                       
        f.close()
        f2.close()

    scriptreplace = {}
    scriptreplace['$OUTPUTFILE$'] = '{0}/ChartData/XPEHH/Chart_{1}_{2:.0f}.png'.format(basepath, dispchromosome, dispcenterposit)
    scriptreplace['$LABELSTRING$'] = 'XPEHH chr={0} pos={1:.0f}'.format(dispchromosome, dispcenterposit)
    scriptreplace['$CENTERPOS$'] = str(dispcenterposit)
    Utils.RunRScript("CreateSNPStatChart_XPEHH", scriptreplace)
 
DrawChart(7,115.0E6,20.0E6)

if (False):#Print all full chromosomes
    for chrnr in range(1,23):
        DrawChart(chrnr,0,800000000)


if (False):#Paper 1 XPEHH window list:
    DrawChart(17,3500000)
    DrawChart(1,115700519)
    DrawChart(1,205501772)
    DrawChart(2,241101317)
    DrawChart(3,194300008)
    DrawChart(6,57700000)
    DrawChart(7,138996715)
    DrawChart(8,106500000)
    DrawChart(9,135296124)
    DrawChart(19,700000)
    DrawChart(19,15300000)
    DrawChart(19,50500000)

print('finished')
