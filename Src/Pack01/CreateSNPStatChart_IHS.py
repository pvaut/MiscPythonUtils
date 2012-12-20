import math
#import sys
import Utils





basepath="C:/Data/Articles/PositiveSelection/DataSaturn"

pops=[]

pops.append({'name':'YRI', 'file':'YRI_650Y_matched_ihs_standardized.txt'})
pops.append({'name':'Malawi', 'file':'Malawi_Untransmitted_ihs_standardized.txt'})
pops.append({'name':'Mandinka', 'file':'Mandinka_Untransmitted_ihs_standardized.txt'})
pops.append({'name':'Wolof', 'file':'Wolof_Untransmitted_ihs_standardized.txt'})
pops.append({'name':'Fula', 'file':'Fula_Untransmitted_ihs_standardized.txt'})
pops.append({'name':'Jola', 'file':'Jola_Untransmitted_ihs_standardized.txt'})
pops.append({'name':'Akan', 'file':'Akan_Untransmitted_ihs_standardized.txt'})
pops.append({'name':'Northerner', 'file':'Northerner_Untransmitted_ihs_standardized.txt'})



def DrawChart(dispchromosome, dispcenterposit, disphalfwidth=7.0E6):
    #main loop over all populations
    for pop in pops:
    
        f = open('{0}/IHS/{1}'.format(basepath, pop['file']))
    
        f2 = open('{0}/ChartData/IHS/{1}.txt'.format(basepath, pop['name']), 'w')
        f2.write('Posit\tStatVal\n') 
        linecount = 0;
        for line in f:
            line = line.rstrip('\r\n')
            cells = line.split("\t")
            chromonr=int(cells[1])
            posit=int(cells[2])
            statval=float(cells[7])
        
            if (chromonr == dispchromosome):
                if (math.fabs(posit - dispcenterposit) <= disphalfwidth):
                    f2.write('{0}\t{1}\n'.format(posit, statval)) 
            
            linecount += 1
            if (linecount % 10000 == 0): print('{0}, {1}'.format(pop['name'], linecount))
                       
        f.close()
        f2.close()

    scriptreplace = {}
    scriptreplace['$OUTPUTFILE$'] = '{0}/ChartData/IHS/Chart_{1}_{2:.0f}.png'.format(basepath, dispchromosome, dispcenterposit)
    scriptreplace['$LABELSTRING$'] = 'IHS chr={0} pos={1:.0f}'.format(dispchromosome, dispcenterposit)
    scriptreplace['$CENTERPOS$'] = str(dispcenterposit)
    Utils.RunRScript("CreateSNPStatChart_IHS", scriptreplace)
 
DrawChart(3,45.0E6,10.0E6)

if (False):#Print all full chromosomes
    for chrnr in range(1,23):
        DrawChart(chrnr,0,800000000)


if (False):
    DrawChart(5,109100000)
    DrawChart(9,137100009)
    DrawChart(11,110100000)
    DrawChart(12,78100000)
    DrawChart(13,47500000)
    DrawChart(16,22900000)
    DrawChart(17,3500000)
    DrawChart(18,64900000)
    DrawChart(19,43500000)
    DrawChart(19,47100000)


print('finished')
