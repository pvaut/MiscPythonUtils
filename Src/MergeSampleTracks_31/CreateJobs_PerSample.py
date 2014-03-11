import Utils.GetSampleList
import os
import glob

def CreateJobs_PerSample(command):
    sampleFiles = Utils.GetSampleList.GetSampleList('{id}.coverage.txt.gz')

    if not(os.path.exists('jobs')):
        os.makedirs('jobs')
    for filename in glob.glob('jobs/*.sh'):
        os.remove(filename)

    if not(os.path.exists('results')):
        os.makedirs('results')
    for filename in glob.glob('results/*'):
        os.remove(filename)

    fll = open('jobs/launcher.sh','w')
    fll.write('#!/bin/bash\n')

    for sampleFile in sampleFiles:
        jobID='JobSample_{0}'.format(sampleFile.replace('/', '_').replace('.', '_'))
        fl=open('jobs/{0}.sh'.format(jobID), 'w')
        fl.write('#!/bin/bash\n')
        fl.write('cd ..\n')
        cmd='python ' + command.format(filename=sampleFile)
        fl.write(cmd+'\n')
        fl.close()
        fll.write('qsub -cwd -V -N {0} {1}.sh\n'.format(jobID, jobID))

    fll.close()
    os.system('chmod +x jobs/launcher.sh')


CreateJobs_PerSample('CreateRegionStats.py {filename}')