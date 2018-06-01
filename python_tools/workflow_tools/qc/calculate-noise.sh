#!/bin/bash

# calculate substituion rate ("noise") for all pileup and pileup-without-duplicates files in the current folder. Run it in a folder with Waltz output


echo -e "Sample\tGenotypeCount\tAltCount\tAltPercent\tContributingSites\tMethod" > noise.txt
echo -e "Sample\tSubstitution\tGenotypeCount\tAltCount\tAltPercent\tContributingSites\tMethod" > noise-by-substitution.txt


for f in `ls $1/*-pileup.txt`
do
  sampleName=`basename $f`
  sampleName=${sampleName/-IGO*/}

  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t";}{max=-1; genotype=-1; total=$5+$6+$7+$8; for(i=5; i<=8; i++){if($i>max){max=$i; genotype=i}} for(i=5; i<=8; i++){if(i==genotype) continue; if($i>=total*0.02) next} genotypeCount+=max; altCount+=(total-max); if(total-max>0){contributingSites++}}END{print sample, genotypeCount, altCount, 100*altCount/(genotypeCount+altCount), contributingSites, "Total" }' $f >> noise.txt

  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; base[5]="A"; base[6]="C"; base[7]="G"; base[8]="T"}{max=-1; genotype=-1; total=$5+$6+$7+$8; for(i=5; i<=8; i++){if($i>max){max=$i; genotype=i}} for(i=5; i<=8; i++){if(i==genotype) continue; if($i>=total*0.02) next}   for(i=5; i<=8; i++){if(i==genotype) continue; substitution=base[genotype]">"base[i]; genotypeCount[substitution]+=max; altCount[substitution]+=$i; if($i>0){contributingSites[substitution]++}}}END{for(s in genotypeCount){g=genotypeCount[s]; a=altCount[s]; c=contributingSites[s]; print sample, s, g, a, 100*a/(g+a), c, "Total"}}' $f >> noise-by-substitution.txt

  g=${f/-pileup.txt/-pileup-without-duplicates.txt}


  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t";}{max=-1; genotype=-1; total=$5+$6+$7+$8; for(i=5; i<=8; i++){if($i>max){max=$i; genotype=i}} for(i=5; i<=8; i++){if(i==genotype) continue; if($i>=total*0.02) next} genotypeCount+=max; altCount+=(total-max); if(total-max>0){contributingSites++}}END{print sample, genotypeCount, altCount, 100*altCount/(genotypeCount+altCount), contributingSites, "Unique" }' $g >> noise.txt

  awk -v sample=$sampleName 'BEGIN{FS=OFS="\t"; base[5]="A"; base[6]="C"; base[7]="G"; base[8]="T"}{max=-1; genotype=-1; total=$5+$6+$7+$8; for(i=5; i<=8; i++){if($i>max){max=$i; genotype=i}} for(i=5; i<=8; i++){if(i==genotype) continue; if($i>=total*0.02) next}   for(i=5; i<=8; i++){if(i==genotype) continue; substitution=base[genotype]">"base[i]; genotypeCount[substitution]+=max; altCount[substitution]+=$i; if($i>0){contributingSites[substitution]++}}}END{for(s in genotypeCount){g=genotypeCount[s]; a=altCount[s]; c=contributingSites[s]; print sample, s, g, a, 100*a/(g+a), c, "Unique"}}' $g >> noise-by-substitution.txt

done
