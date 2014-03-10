import Utils.GetSampleList
import os
import glob

def CreateJobs_PerSample(command):
    sampleFiles = Utils.GetSampleList.GetSampleList('{id}.coverage.txt.gz')

    if not(os.path.exists('jobs')):
        os.makedirs('jobs')

    for filename in glob.glob('jobs/*.sh'):
        os.remove(filename)

    fll = open('jobs/launcher.sh','w')
    fll.write('#!/bin/bash\n')

    for sampleFile in sampleFiles:
        jobID='JobSample_{0}'.format(sampleFile.replace('/', '_').replace('.', '_'))
        cmd='python ../' + command.format(filename=sampleFile)
        fl=open('jobs/{0}.sh'.format(jobID), 'w')
        fl.write('#!/bin/bash\n')
        fl.write(cmd+'\n')
        fl.close()
        fll.write('qsub -cwd -V -N {0} {1}.sh\n'.format(jobID, jobID))

    fll.close()
    os.system('chmod +x jobs/launcher.sh')


CreateJobs_PerSample('QuantileTracks.py {filename}')