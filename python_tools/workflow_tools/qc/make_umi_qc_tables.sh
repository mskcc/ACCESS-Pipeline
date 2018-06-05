#!/bin/bash

set -x

# $1 - A-positions file
# $2 - B-positions file
# $3: - The collapsed bam folders that contain collapsed bams, collapsed fastqs and first-pass.txt.


# make output files
echo -e "ClusterSize\tSample" > cluster-sizes.txt
echo -e "ClusterSize\tSample" > cluster-sizes-post-filtering.txt
echo -e "Clusters\tSample" > clusters-per-position.txt
echo -e "Clusters\tSample" > clusters-per-position-post-filtering.txt
echo -e "Sample\tType\tCount" > family-types-A.txt
echo -e "Sample\tType\tCount" > family-types-B.txt

# link up the on target positions file
ln -s $1 A-positions.txt
ln -s $2 B-positions.txt

# process samples
for sampleFolder in "${@:3}"
do
  sampleName=`basename $sampleFolder`
  sampleName=${sampleName/-IGO*/}

  # cluster sizes
  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos}}{if(positions[$1"\t"$2]!=null) print $4+$5, sample}' $sampleFolder/first-pass.txt >> cluster-sizes.txt

  # really need to think about this!!!
  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos}}{if(positions[$1"\t"$2]!=null && $4>=1 && $5>=1) print $4+$5, sample}' $sampleFolder/first-pass.txt >> cluster-sizes-post-filtering.txt

  # cluster sizes post filtering
  #gunzip -c $sampleFolder/collapsed_R1_.fastq.gz | grep "@Marianas" | awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos} FS=":"}{if(positions[$3"\t"$4]!=null) print $5+$6, sample}' >> cluster-sizes-post-filtering.txt

  # clusters per position
  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos}}{if(positions[$1"\t"$2]!=null) print $1"AND"$2}' $sampleFolder/first-pass.txt | sort | uniq -c | awk -v sample=$sampleName '{print $1"\t"sample}' >> clusters-per-position.txt

  # clusters per position post filtering
  gunzip -c $sampleFolder/collapsed_R1_.fastq.gz | grep "@Marianas" | awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos} FS=":"}{if(positions[$3"\t"$4]!=null) print $3"AND"$4}' | sort | uniq -c | awk -v sample=$sampleName '{print $1"\t"sample}' >> clusters-per-position-post-filtering.txt

  # calculate A pool family counts
  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){positions[$1"\t"$2]=$1"\t"$2}}{if(positions[$1"\t"$2]==null) next; if($4+$5==1){singletons++} else if(($4==0 || $5==0) && $4+$5==2){subSimplex++} else if(($4==0 || $5==0) && $4+$5>=3){simplex++} else if($4>0 && $5>0){duplex++}}END{print sample, "Singletons", singletons; print sample, "Sub-Simplex", subSimplex; print sample, "Simplex", simplex; print sample, "Duplex", duplex}' $sampleFolder/first-pass.txt >> family-types-A.txt

  # calculate B pool family counts
  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "B-positions.txt"){positions[$1"\t"$2]=$1"\t"$2}}{if(positions[$1"\t"$2]==null) next; if($4+$5==1){singletons++} else if(($4==0 || $5==0) && $4+$5==2){subSimplex++} else if(($4==0 || $5==0) && $4+$5>=3){simplex++} else if($4>0 && $5>0){duplex++}}END{print sample, "Singletons", singletons; print sample, "Sub-Simplex", subSimplex; print sample, "Simplex", simplex; print sample, "Duplex", duplex}' $sampleFolder/first-pass.txt >> family-types-B.txt

done
