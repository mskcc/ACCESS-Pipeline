#!/bin/bash

# Process the given UMI bam file and generate collapsed fatsqs and stats

# $1 - UMI bam file to be processed
# $2 - normal pileup file corresponding to the bam file (made with correct bed file)


export TMPDIR=/ifs/work/scratch


java="/opt/common/CentOS_6/java/jdk1.8.0_31/bin/java"
referenceFasta=~/resources/impact-GRCh37/Homo_sapiens_assembly19.fasta
minMappingQuality="1"
minBaseQuality="30"
mismatches="1"
wobble="2"
minConsensusPercent="90"
jarFile="$HOME/software/Marianas.jar"


echo -e "minMappingQuality=$minMappingQuality, minBaseQuality=$minBaseQuality, mismatches=$mismatches, wobble=$wobble, minConsensusPercent=$minConsensusPercent"

bam=$1
pileup=$2
sample=`basename $bam`
sample=${sample/.bam}


# pass 1
echo -e "`date` Pass 1"
$java -server -Xms8g -Xmx8g -cp $jarFile org.mskcc.marianas.umi.duplex.DuplexUMIBamToCollapsedFastqFirstPass $bam $pileup $minMappingQuality $minBaseQuality $mismatches $wobble $minConsensusPercent $referenceFasta .


# sort the first pass output by mate position
echo -e "`date` Sorting first-pass.txt"
sort -S 8G -k 6,6n -k 8,8n first-pass.txt > first-pass.mate-position-sorted.txt


# pass 2
echo -e "`date` Pass 2"
$java -server -Xms8g -Xmx8g -cp $jarFile org.mskcc.marianas.umi.duplex.DuplexUMIBamToCollapsedFastqSecondPass $bam $pileup $minMappingQuality $minBaseQuality $mismatches $wobble $minConsensusPercent $referenceFasta .

# delete unnecessory files
# rm first-pass.mate-position-sorted.txt

# gzip
echo -e "`date` Compressing fastqs"
gzip collapsed_R1_.fastq
gzip collapsed_R2_.fastq


# make collapsed bam
echo -e "`date` Running juber-fastq-to-bam.sh "
~/software/bin/juber-fastq-to-bam.sh collapsed_R1_.fastq.gz no


# separate duplex and simplex-duplex bams
echo -e "`date` Separating simplex-duplex and duplex bams "
$java -server -Xms8g -Xmx8g -cp $jarFile org.mskcc.marianas.umi.duplex.postprocessing.SeparateBams collapsed.bam

