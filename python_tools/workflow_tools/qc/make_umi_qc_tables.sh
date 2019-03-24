#!/bin/bash

# $1 - A-on-target-positions file with chromosome and position separated by tab

# $2 - B-on-target-positions with chromosome and position separated by tab

# $3: - The sample folders that contain collapsed bams, collapsed fastqs and first-pass.txt

set -x

# make links
ln -s `readlink -e $1` A-positions.txt
ln -s `readlink -e $2` B-positions.txt


# make output files
echo -e 'FamilySize\tFamilyType\tFrequency\tSample' > family-sizes.txt
#echo -e "Clusters\tSample" > families-per-position.txt
echo -e 'Sample\tType\tCount' > family-types-A.txt
echo -e 'Sample\tType\tCount' > family-types-B.txt


# process samples
for sampleFolder in "${@:3}"
do
  sampleName=`basename $sampleFolder`

  # family sizes
  gunzip -c $sampleFolder/collapsed_R1_.fastq.gz | grep "@Marianas" | awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos} FS=":"}{if(positions[$3"\t"($4+20)]==null) next; if($5!=0 && $6!=0 && $9!=0 && $10!=0) type="Duplex"; else if($5+$6<=2 || $9+$10<=2) type="SingletonOrSubSimplex"; else type="Simplex"; key=$5+$6"\t"type; freqs[key]++; allKey=$5+$6"\tAll"; allFreqs[allKey]++;}END{ for(key in freqs) print key, freqs[key], sample; for(key in allFreqs) print key, allFreqs[key], sample}' >> family-sizes.txt

  #print $5+$6, $9+$10, type, sample

  # sample 10% of the lines
  #numLines=$((`wc -l family-sizes-temp.txt | awk '{print $1}'`/10))
  #shuf -n $numLines family-sizes-temp.txt >> family-sizes.txt
  #rm family-sizes-temp.txt

  # old
  #awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos}}{if(positions[$1"\t"$2]!=null) print $4+$5, sample}' $sampleFolder/first-pass.txt >> cluster-sizes.txt

  # clusters per position
  #awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos}}{if(positions[$1"\t"$2]!=null) print $1"AND"$2}' $sampleFolder/first-pass.txt | sort | uniq -c | awk -v sample=$sampleName '{print $1"\t"sample}' >> families-per-position.txt

  # calculate family counts
  gunzip -c $sampleFolder/collapsed_R1_.fastq.gz | grep "@Marianas" | awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){pos=$1"\t"$2; positions[pos]=pos} FS=":"}{if(positions[$3"\t"($4+20)]==null) next; if($5!=0 && $6!=0 && $9!=0 && $10!=0) duplex++; else if($5+$6==1 || $9+$10==1) singletons++; else if($5+$6==2 || $9+$10==2) subSimplex++; else simplex++}END{print sample, "Singletons", singletons; print sample, "Sub-Simplex", subSimplex; print sample, "Simplex", simplex; print sample, "Duplex", duplex}' >> family-types-A.txt

  gunzip -c $sampleFolder/collapsed_R1_.fastq.gz | grep "@Marianas" | awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "B-positions.txt"){pos=$1"\t"$2; positions[pos]=pos} FS=":"}{if(positions[$3"\t"($4+20)]==null) next; if($5!=0 && $6!=0 && $9!=0 && $10!=0) duplex++; else if($5+$6==1 || $9+$10==1) singletons++; else if($5+$6==2 || $9+$10==2) subSimplex++; else simplex++}END{print sample, "Singletons", singletons; print sample, "Sub-Simplex", subSimplex; print sample, "Simplex", simplex; print sample, "Duplex", duplex}' >> family-types-B.txt

  # old
  #awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; while(getline < "A-positions.txt"){positions[$1"\t"$2]=$1"\t"$2}}{if(positions[$1"\t"$2]==null) next; if($4+$5==1){singletons++} else if(($4==0 || $5==0) && $4+$5==2){subSimplex++} else if(($4==0 || $5==0) && $4+$5>=3){simplex++} else if($4>0 && $5>0){duplex++}}END{print sample, "Singletons", singletons; print sample, "Sub-Simplex", subSimplex; print sample, "Simplex", simplex; print sample, "Duplex", duplex}' $sampleFolder/first-pass.txt >> family-types-A.txt

done
