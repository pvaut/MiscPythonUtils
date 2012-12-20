import os

def utils(x):
    return(x/2)

rexecpath="C:/Software/R/bin/x64/R.exe"
rscriptpath='C:/Users/pvaut/workspace/PythonTest01'
 
def RunRScript(scriptname,replacetokens):
    f = open(rscriptpath+"/"+scriptname+".R")
    script=f.read();
    f.close()
    for replacetoken in replacetokens:
        script=script.replace(replacetoken,replacetokens[replacetoken])
    outputscriptname=rscriptpath+"/Tmp.R"
    f = open(outputscriptname,'w')
    f.write(script)
    f.close()
    os.system(rexecpath+" CMD BATCH "+rscriptpath+"/Tmp.R")
