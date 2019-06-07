'''
Created 09 December 2018
ptashkir@mskcc.org
wrapper for cfdna copy number pipeline
#######################################
to do:
take single bed file and calculate GC of intervals at run time
incoporate off target intervals, if needed

'''

import argparse
import os
import re
import sys
import time
import stat
import csv
from subprocess import Popen
import shlex
import pysam
import pandas as pd
from joblib import Parallel, delayed

def main():
    parser = argparse.ArgumentParser(prog='cfdna_scna.py', description='cfdna copy number pipeline wrapper', usage='%(prog)s [options]')
    parser.add_argument("-t", "--tumorManifest", action="store", dest="tumorManifest", required=True, metavar='tumors.txt', help="Full path to the tumor sample manifest, tab serparated BAM path, patient sex.")
    parser.add_argument("-n", "--normalManifest", action="store", dest="normalManifest", required=True, metavar='normals.txt', help="Full path to the normal sample manifest, tab serparated BAM path, patient sex.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=True, help="make lots of noise [default]")
    parser.add_argument("-tr", "--threads", action="store", dest="threads", required=False, metavar='8', default='8', help="Number of Threads to be used to generate coverage metrics")
    parser.add_argument("-b", "--bedTargets", action="store", dest="TARGETS", required=True, metavar='/somepath/ACCESS_targets_coverage.bed', help="Full Path to BED file of panel targets")
    parser.add_argument("-ta", "--targetAnnotations", action="store", dest="ANNOTATIONS", required=True, metavar='/somepath/ACCESS_targets_coverage.txt', help="Full Path to text file of target annotations. Columns = (Chrom, Start, End, Target, GC_150bp, GeneExon,Cyt,Interval)")
    parser.add_argument("-g", "--genomeReference", action="store", dest="GENOME", required=True, metavar='/somepath/Homo_Sapeins_hg19.fasta', help="Full Path to the reference fasta file.")
    parser.add_argument("-r", "--RPATH", action="store", dest="R", required=True, metavar='/somepath/R', help="Path to R executable.")
    parser.add_argument("-q", "--queue", action="store", dest="queue", required=True, metavar='test.q or clin2.q', help="Name of the SGE queue")
    parser.add_argument("-id", "--runID", action="store", dest="runID", required=True, metavar='ACCESSv1-VAL-20180001', help="name of runID.")
    parser.add_argument("-o", "--outDir", action="store", dest="outdir", required=True, metavar='/somepath/output', help="Full Path to the output dir.")
    parser.add_argument("-l", "--loess", action="store", dest="loess", required=True, metavar='/somepath/loessnormalize_nomapq_cfdna.R', help="Full Path to the loess normalization R script.")
    parser.add_argument("-cn", "--copynumber", action="store", dest="cnAnalysis", required=True, metavar='/somepath/copynumber_tm.batchdiff_cfdna.R', help="Full Path to the copy number R script.")
    parser.add_argument("-qsub", "--qsubPath", action="store", dest="qsub", required=False, metavar='/somepath/qsub', help="Full Path to the qsub executables of SGE.")
    parser.add_argument("-bsub", "--bsubPath", action="store", dest="bsub", required=False, metavar='/somepath/bsub', help="Full Path to the bsub executables of LSF.")
    parser.add_argument("-gatk", "--GATK", action="store", dest="GATK", required=False, metavar='/somepath/GATK', help="Full Path to the GATK.")
    parser.add_argument("-j", "--javaPATH", action="store", dest="JAVA", required=False, metavar='/somepath/java', help="Path to java executable.")

    print "Running the cfdna copy number pipeline."
    sys.stdout.flush()
    args = parser.parse_args()
    threads= int(args.threads)

    with Parallel(n_jobs=threads,verbose=1) as parallel:
        (patientSex)= ProcessArgs(args)

        (tumorCovFile) = RunBedCov(args,'tumor_bams.list', 'tumors',parallel)
        (normalCovFile) = RunBedCov(args,'normal_bams.list', 'normals',parallel)

        (normalLoessFile) = RunLoessNormalization(args, normalCovFile, 'normal')
        (tumorLoessFile) = RunLoessNormalization(args, tumorCovFile, 'tumor')

        RunTumorCN(args, normalLoessFile, tumorLoessFile)

def ProcessArgs(args):

    tumorBamFiles = []
    normalBamFiles = []
    patientSex={}
    if(args.verbose):
        print "Going to see how many bam files are there for us to run the analysis."
        sys.stdout.flush()

    if(args.qsub and args.bsub):
        print "Please give either qsub or bsub arguments. Script does not allow usage of both\n"
        sys.exit(1)
    if((not args.qsub) and (not args.bsub)):
        print "Please give either qsub or bsub arguments. None are provided\n"
        sys.exit(1)

    with open(args.tumorManifest, 'r') as tfile:
        tlist= open('tumor_bams.list', 'w')
        for line in tfile:
            data = line.rstrip('\n')
            bfile = re.split('\t', data)[0]
            sex = re.split('\t', data)[1]
            tumorBamFiles.append(bfile)
            patientSex.update({bfile:sex})
            tlist.write(bfile+"\n")
        tlist.close()

    with open(args.normalManifest, 'r') as nfile:
        nlist= open('normal_bams.list', 'w')
        for line in nfile:
            data = line.rstrip('\n')
            bfile = re.split('\t', data)[0]
            normalBamFiles.append(bfile)
            sex = re.split('\t', data)[1]
            patientSex.update({bfile:sex})
            nlist.write(bfile+"\n")
        nlist.close()

    if(args.verbose):
        print "Going to run analysis for", tumorBamFiles.__len__(), " tumor BAM files using ", normalBamFiles.__len__()," normal BAM files"

    return(patientSex)


def RunBedCov(args,bamlist, runType, parallel):
    if(args.verbose):
        print "generating coverage metrics for " +runType+ " BAMS using pysam bedcov"
        sys.stdout.flush()

    covFile = args.runID + "_" +runType+ "_targets_nomapq.covg_interval_summary"

    if os.path.exists(covFile):
        print "Coverage analysis file " + covFile + " already exists, will not generate coverage metrics"
        return(covFile)

    bfile = open(bamlist)
    bed = args.TARGETS

    outname = args.runID + "_" +runType+ "_targets_nomapq.covg"
    cov_args = []
    for line in bfile:
        for bam in line.split():
            cov_args.append((bam, bed))

    results = parallel(map(delayed(parallelCov), cov_args))
    results= {k: v for x in results for k, v in x.items()}

    df= pd.DataFrame.from_records(results, index='Target')
    df.to_csv(covFile, sep='\t')

    if os.path.isfile(covFile):
        print "Completed generation of coverage metrics for " +runType+ " BAMS using pysam bedcov"
        return(covFile)
    else:
        print "Coverage file " + covFile + "does note exist, something went wrong here"

def parallelCov(cov_args):
    (bam,bed) = cov_args
    sampleCov=[]
    output={}
    mq = 0 #can param min mapping quality if desired
    id= re.sub('.*\/(.*)_cl.*',r'\1', bam)
    print "Generating coverage metrics for: " + id
    sys.stdout.flush()
    id = id+"_mean_cvg"
    cmd = [bed, bam]
    cmd.extend(['-Q',bytes(mq)])

    bstring = pysam.bedcov(*cmd, split_lines=False)
    lines = bstring.splitlines()
    targets=[]
    for line in lines:
        fields = line.split('\t')
        chr = fields[0]
        start = int(fields[1])
        end= int(fields[2])
        target = fields[3]
        coverage = int(fields[4])
        intlen = float(end - start)
        meancov = str(coverage / intlen)
        target = chr +":"+str(start)+"-"+str(end)
        targets.append(target)
        sampleCov.append(meancov)
    output.update({id:sampleCov})
    output.update({'Target':targets})
    return(output)

def RunLoessNormalization(args, covFile, runType):
    loessFile = args.runID + "_" + runType + "_ALL_intervalnomapqcoverage_loess.txt"

    if(args.verbose):
        print "running loess normalization"
        sys.stdout.flush()

    cmd = args.R + " --slave --vanilla --args " + args.runID+ " " + args.outdir + " " + args.ANNOTATIONS + " " + covFile + " " + runType + "< " + args.loess

    cl_cmd =''
    mem = 8
    maxmem = int(mem)+8
    if(args.qsub):
        cl_cmd = args.qsub + " -q " + args.queue + " -N " + "loessNorm" + " -V -l h_vmem=8G,virtual_free=8G -pe smp 1 -wd " + args.outdir + " -sync y " + " -b y " + cmd
        print "CLUSTER_CMD loess==>", cl_cmd , "\n"

    else:
        cl_cmd= args.bsub + " -q " + args.queue + " -J " + "loessNorm" + " -o loessNorm.%J.out -e loessNorm.%J.err" + " -We 24:00 -R \"rusage[mem=" + str(mem) + "]\" -M " + str(maxmem) + " -n 1 " + " -cwd " + args.outdir + ' -K  "' + cmd + '"'
        print "CLUSTER_CMD loess==>", cl_cmd , "\n"
    cl_args = shlex.split(cl_cmd)
    proc = Popen(cl_args)
    proc.wait()
    retcode = proc.returncode
    if(retcode == 0):
        if(args.verbose):
            print "Finished Running loess normalization for " + runType + " BAM files"
    else:
        if(args.verbose):
            print "loess normalization is either still running or it errored out with return code", retcode,"\n"

    if os.path.isfile(loessFile):
        return(loessFile)
    else:
        print "Loess normalization file " + loessFile + " does not exist, something went wrong here"


def RunTumorCN(args,normalLoessFile, tumorLoessFile):
    if(args.verbose):
        print "calculating log ratio, performing segmentation and plot fest!"
        sys.stdout.flush()

    cmd = args.R + " --slave --vanilla --args " + args.runID+ " " + normalLoessFile + " " + args.ANNOTATIONS + " " + tumorLoessFile + " MIN "+ "< " + args.cnAnalysis

    cl_cmd =''
    mem = 8
    maxmem = int(mem)+8
    if(args.qsub):
        cl_cmd = args.qsub + " -q " + args.queue + " -N " + "runCN" + " -V -l h_vmem=8G,virtual_free=8G -pe smp 1 -wd " + args.outdir + " -sync y " + "-b y " + cmd
        print "CLUSTER_CMD CN==>", cl_cmd , "\n"

    else:
        cl_cmd= args.bsub + " -q " + args.queue + " -J " + "runCN" + " -o runCN.%J.out -e runCN.%J.err"+ " -We 24:00 -R \"rusage[mem=" + str(mem) + "]\" -M " + str(maxmem) + " -n 1 " + " -cwd " + args.outdir + ' -K "' + cmd + '"'
        print "CLUSTER_CMD CN==>", cl_cmd , "\n"
    cl_args = shlex.split(cl_cmd)
    proc = Popen(cl_args)
    proc.wait()
    retcode = proc.returncode
    if(retcode == 0):
        if(args.verbose):
            print "Finished Running segmentation and plotting"
            print "Done running Copy Number pipeline."
    else:
        if(args.verbose):
            print "copy number analysis is either still running or it errored out with return code", retcode,"\n"


def RunCoverage(args): #this method is now depricated
    if(args.verbose):
        print "generating coverage metrics for BAMS"

    cmd_t = args.JAVA + " -Djava.io.tmpdir=/dmp/analysis/SCRATCH -Xmx4g -jar " + args.GATK + " -T DepthOfCoverage -R " + args.GENOME + " -I tumor_bams.list"  + " -o " + args.runID + "_tumors_targets_nomapq.covg" + " -L " + args.TARGETS + " -rf BadCigar -mmq 0 -mbq 20 -omitLocusTable -omitSampleSummary -omitBaseOutput --allow_potentially_misencoded_quality_scores"
    cmd_n = args.JAVA + " -Djava.io.tmpdir=/dmp/analysis/SCRATCH -Xmx4g -jar " + args.GATK + " -T DepthOfCoverage -R " + args.GENOME + " -I normal_bams.list"  + " -o " + args.runID + "_normals_targets_nomapq.covg" + " -L " + args.TARGETS + " -rf BadCigar -mmq 0 -mbq 20 -omitLocusTable -omitSampleSummary -omitBaseOutput --allow_potentially_misencoded_quality_scores"

    cl_cmd_t = ''
    cl_cmd_n = ''

    mem = int(args.threads) * 8
    maxmem = int(mem)+8
    if(args.qsub):
        cl_cmd_t = args.qsub + " -q " + args.queue + " -N " + "DOC_tumors" + " -V -l h_vmem=8G,virtual_free=8G -pe smp " + args.threads + " -wd " + args.outdir + " -sync y " + " -b y " + cmd_t
        cl_cmd_n = args.qsub + " -q " + args.queue + " -N " + "DOC_normals" + " -V -l h_vmem=8G,virtual_free=8G -pe smp " + args.threads + " -wd " + args.outdir + " -sync y " + " -b y " + cmd_n
    else:
        cl_cmd_t = args.bsub + " -q " + args.queue + " -J " + "DOC_tumors" + " -We 24:00 -R \"rusage[mem=" + str(mem) + "]\" -M " + str(maxmem) + " -n " + args.threads + " -cwd " + args.outdir + " -K " + cmd_t
        cl_cmd_n = args.bsub + " -q " + args.queue + " -J " + "DOC_tumors" + " -We 24:00 -R \"rusage[mem=" + str(mem) + "]\" -M " + str(maxmem) + " -n " + args.threads + " -cwd " + args.outdir + " -K " + cmd_n


    tumorCovFile = args.outdir + "/"+ args.runID + "_tumors_targets_nomapq.covg.sample_interval_summary"
    normalCovFile = args.outdir + "/"+ args.runID + "_normals_targets_nomapq.covg.sample_interval_summary"

    if os.path.exists(tumorCovFile):
        print "Coverage analysis for tumor bams already exist, will not run"

    else:
        print "CLUSTER_CMD tumors==>", cl_cmd_t , "\n"
        cl_args_t = shlex.split(cl_cmd_t)
        proct = Popen(cl_args_t)
        proct.wait()
        retcodet = proct.returncode
        if(retcodet == 0):
            if(args.verbose):
                print "Finished Running coverage analysis for tumor bams "
        else:
            if(args.verbose):
                print "coverage analysis is either still running or it errored out with return code", retcode,"\n"

    if os.path.exists(normalCovFile):
        print "Coverage analysis for normal bams already exist, will not run"
    else:
        print "CLUSTER_CMD normals==>", cl_cmd_n , "\n"
        cl_args_n = shlex.split(cl_cmd_n)
        procn = Popen(cl_args_n)
        procn.wait()
        retcoden = procn.returncode
        if(retcoden == 0):
            if(args.verbose):
                print "Finished Running coverage analysis for normal bams "
        else:
            if(args.verbose):
                print "coverage analysis is either still running or it errored out with return code", retcode,"\n"

    files = [normalCovFile,tumorCovFile]
    if os.path.isfile(normalCovFile and tumorCovFile):
        return(tumorCovFile, normalCovFile)
    else:
        print "Tumor and Normal BAM coverage files do not exist, something went wrong here"


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print("Elapsed time was %g seconds" % (end_time - start_time))
