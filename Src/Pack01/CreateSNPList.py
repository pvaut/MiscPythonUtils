
basepath="C:/Data/Articles/PositiveSelection/DataSaturn"

snpdict={}

#look up snps for IHS
pops1=[]
pops1.append({'name':'YRI', 'files':['YRI_650Y_matched_ihs_standardized.txt']})
pops1.append({'name':'Malawi', 'files':['Malawi_Untransmitted_ihs_standardized.txt']})
pops1.append({'name':'Mandinka', 'files':['Mandinka_Untransmitted_ihs_standardized.txt']})
pops1.append({'name':'Wolof', 'files':['Wolof_Untransmitted_ihs_standardized.txt']})
pops1.append({'name':'Fula', 'files':['Fula_Untransmitted_ihs_standardized.txt']})
pops1.append({'name':'Jola', 'files':['Jola_Untransmitted_ihs_standardized.txt']})
pops1.append({'name':'Akan', 'files':['Akan_Untransmitted_ihs_standardized.txt']})
pops1.append({'name':'Northerner', 'files':['Northerner_Untransmitted_ihs_standardized.txt']})
linecount=0
for pop in pops1:
    #scan all files associated with this population
    for file in pop['files']:
        f = open(basepath+"/IHS/"+file)
        linecount=0;
        for line in f:
            line=line.rstrip('\r\n')
            cells=line.split("\t")
            snpname=cells[0]
            chromonr=int(cells[1])
            posit=int(cells[2])
            snpdict[snpname]=[chromonr,posit]
            linecount+=1
            if (linecount%10000==0): print(linecount)
        f.close()
        

#look up snps for XPEHH
pops2=[]
pops2.append({'name':'YRI',        'files':['CEU_Reference/CEU_YRI_650Y_XP_EHH_standardized.txt']        , 'sign':-1 })
pops2.append({'name':'Malawi',     'files':['CEU_Reference/CEU_Malawi_650Y_XP_EHH_standardized.txt']     , 'sign':-1 })
pops2.append({'name':'Mandinka',   'files':['CEU_Reference/CEU_Mandinka_650Y_XP_EHH_standardized.txt']   , 'sign':-1 })
pops2.append({'name':'Wolof',      'files':['CEU_Reference/CEU_Wolof_650Y_XP_EHH_standardized.txt']      , 'sign':-1 })
pops2.append({'name':'Fula',       'files':['CEU_Reference/CEU_Fula_650Y_XP_EHH_standardized.txt']       , 'sign':-1 })
pops2.append({'name':'Jola',       'files':['CEU_Reference/CEU_Jola_650Y_XP_EHH_standardized.txt']       , 'sign':-1 })
pops2.append({'name':'Akan',       'files':['CEU_Reference/CEU_Akan_650Y_XP_EHH_standardized.txt']       , 'sign':-1 })
pops2.append({'name':'Northerner', 'files':['CEU_Reference/CEU_Northerner_650Y_XP_EHH_standardized.txt'] , 'sign':-1 })
#main loop over all populations
for pop in pops2:
    mysign=pop['sign']
    #scan all files associated with this population
    for file in pop['files']:
        f = open(basepath+"/XPEHH/"+file)
        linecount=0;
        for line in f:
            line=line.rstrip('\r\n')
            cells=line.split("\t")
            chromonr=int(cells[0])
            snpname=cells[1]
            posit=int(cells[2])
            #if not(snpname in snpdict): raise Exception("Dju!")
            snpdict[snpname]=[chromonr,posit]
        f.close()

        
       
f=open(basepath+"/_PV_SNPList.txt",'w') 
for snp in snpdict:
    chromo=snpdict[snp][0]
    posit=snpdict[snp][1]
    f.write("chr{0}\t{1}\t{2}\t{3}\n".format(chromo,posit-100,posit+100,snp))
f.close()
        
print("finished!")
