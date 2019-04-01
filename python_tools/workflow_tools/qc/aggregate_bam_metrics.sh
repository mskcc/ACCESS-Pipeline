#!/bin/bash

set -x


# Copy inputs to the current dir,
# until cwl has support for InitialWorkDirRequirement with
# directories, or a list of files.
#
# https://github.com/common-workflow-language/cwltool/issues/282
cp $1/* .


# process *.read-counts files to get on-target vs off-target
cat *.read-counts > read-counts.txt
printf "Bam\tCMO_SAMPLE_ID\tTotalReads\tUnmappedReads\tTotalMapped\tUniqueMapped\tDuplicateFraction\tTotalOnTarget\tUniqueOnTarget\tTotalOnTargetFraction\tUniqueOnTargetFraction\n" > t
# add ID
awk 'BEGIN{FS=OFS="\t"}{ split($1, a, "_cl_aln_srt"); $1=$1"\t"a[1]; print }' read-counts.txt >> t
mv t read-counts.txt


# process *.fragment-sizes files
printf "FragmentSize\tTotalFrequency\tUniqueFrequency\tCMO_SAMPLE_ID\n" > t
for f in `ls *.fragment-sizes`
do
  sample="${f/.bam.fragment-sizes/}"
  sample=`echo $sample | awk 'BEGIN{FS="_cl_aln_srt"}{print $1}'`

  awk -v sample=$sample 'BEGIN{FS=OFS="\t"}{$3=$3"\t"sample; print}' $f >> t

done

mv t fragment-sizes.txt


# process coverage
printf "CMO_SAMPLE_ID\tTotalCoverage\tUniqueCoverage\n" > waltz-coverage.txt

# collect mean coverage from Waltz Metrics output
for f in `ls *-intervals.txt`
do
  sample="${f/-intervals.txt/}"
  sample=`echo $sample | awk 'BEGIN{FS="_cl_aln_srt"}{print $1}'`
  printf "$sample\t" >> waltz-coverage.txt

  totalCovarege=`awk 'BEGIN{FS=OFS="\t"}{L=L+$5; coverage=coverage+$5*$7;}END{print coverage/L}' $f`
  uniqueCovarege=`awk 'BEGIN{FS=OFS="\t"}{L=L+$5; coverage=coverage+$5*$7;}END{print coverage/L}' ${f/-intervals/-intervals-without-duplicates}`

  printf "$totalCovarege\t$uniqueCovarege\n" >> waltz-coverage.txt

done

# calculate per interval sum of coverage across all samples, both with and without duplicates
cat *-intervals.txt | awk 'BEGIN{FS=OFS="\t"; OFMT = "%.0f"}{ key=$1"\t"$2"\t"$3"\t"$4"\t"$5; value=coverage[key]; if(value==null){coverage[key]=$7; gc[key]=$8}else{coverage[key]=value+$7}}END{for(i in coverage){print i, gc[i], coverage[i]}}' | sort -k 4,4 > t1

cat *-intervals-without-duplicates.txt | awk 'BEGIN{FS=OFS="\t"; OFMT = "%.0f"}{ key=$4; value=coverage[key]; if(value==null){coverage[key]=$7;}else{coverage[key]=value+$7}}END{for(i in coverage){print i, coverage[i]}}' | sort -k 1,1 > t2

# put them in the same file
printf "Chr\tStart\tEnd\tIntervalName\tLength\tGC\tCoverage\tCoverageWithoutDuplicates\n" > intervals-coverage-sum.txt
awk 'BEGIN{FS=OFS="\t"; OFMT = "%.0f"}{getline line < "t1"; print line, $2}' t2 >> intervals-coverage-sum.txt
rm t1 t2

# collect per sample per interval coverage from LocusPocus Metrics output
printf "Interval\tCMO_SAMPLE_ID\tTotalCoverage\tGC\n" > t5
printf "Interval\tCMO_SAMPLE_ID\tUniqueCoverage\tGC\n" > t6

for f in `ls *-intervals.txt`
do
  sample="${f/-intervals.txt/}"
  sample=`echo $sample | awk 'BEGIN{FS="_cl_aln_srt"}{print $1}'`
  awk -v sample=$sample 'BEGIN{FS=OFS="\t"; OFMT = "%.0f"}{ print $4, sample, $7, $8}' $f >> t5
  awk -v sample=$sample 'BEGIN{FS=OFS="\t"; OFMT = "%.0f"}{ print $4, sample, $7, $8}'  ${f/-intervals/-intervals-without-duplicates} >> t6
done


######### Normalize coverage within sample and across samples and create R-friendly files

printf "Interval\tGene\tCMO_SAMPLE_ID\tTotalCoverage\n" > t7
printf "Interval\tGene\tCMO_SAMPLE_ID\tUniqueCoverage\n" > t8

for f in `ls *-intervals.txt`
do
  sample="${f/-intervals.txt/}"
  sample=`echo $sample | awk 'BEGIN{FS="_cl_aln_srt"}{print $1}'`

  # do only intra-sample normalization
  # sample mean as the normalizing factor
  normFactor=`awk 'BEGIN{FS=OFS="\t"}{intervals++; coverage+=$7;}END{print coverage/intervals}' $f`
  # sample median as the normalizing factor
  #normFactor=`awk 'BEGIN{FS=OFS="\t"}{values[NR]=$7}END{asort(values); if(NR%2==1){print values[(NR+1)/2]} else {print (values[NR/2] + values[(NR/2)+1])/2.0}}' $f`
  awk -v sample=$sample -v normFactor=$normFactor 'BEGIN{FS=OFS="\t"}{split($4, a, "_"); print $4, a[1], sample, $7/normFactor;}' $f >> t7

  # use both inter-sample and intra sample normalization
  #awk -v sample=$sample 'BEGIN{FS=OFS="\t"; while(getline < "locuspocus-coverage.txt"){if($1==sample) sampleCoefficient=1/$2}}{split($4, a, "_"); print $4, a[1], sample, $7*sampleCoefficient;}' $f > t
  #awk 'BEGIN{FS=OFS="\t"; while(getline < "t"){total+=$4}}{split($4, a, "_"); print $1, $2, $3, $4/total}' t >> t7

  # sample mean as the normalizing factor
  normFactor=`awk 'BEGIN{FS=OFS="\t"}{intervals++; coverage+=$7;}END{print coverage/intervals}' ${f/-intervals/-intervals-without-duplicates}`
  awk -v sample=$sample -v normFactor=$normFactor 'BEGIN{FS=OFS="\t";}{split($4, a, "_"); print $4, a[1], sample, $7/normFactor}'  ${f/-intervals/-intervals-without-duplicates} >> t8
done

echo -e "Done."










#
