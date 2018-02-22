# Pick your bed file:
# bedFile=/home/patelju1/workspace/Waltz/bedFiles/pan-cancer-panel.bed
# bedFile=/home/patelju1/workspace/Waltz/bedFiles/PanCancer_v2_0_probe_A.bed


# Run Vardict with modified parameters

bsub
-R “rusage[mem=30]”
-M 26
-We 0:59
-oo cmo_vardict-log.txt
cmo_vardict
-f 0.0002
-G GRCh37
-b $tumorBam
-b2 $normalBam
-N $tumorName
-N2 $normalName
--vcf vardict.vcf
-c1
-S2
-E3
-g4 $bedFile
-r 1
> job.txt


# Convert Vardict vcf to maf:
jobID=`cat job.txt | cut -d"<" -f2 | cut -d">" -f1`
bsub -R “rusage[mem=30]” -M 26 -We 0:59 -w ${jobID}
-oo vcf2maf.log
cmo_vcf2maf
--input-vcf vardict.vcf
--output-maf vardict_retainSTATUS.maf
--tumor-id ${tumorName}
--normal-id $normalName
--vcf-tumor-id ${tumorName}
--vcf-normal-id ${normalName}


# Generate the fillout (this should utilize bsub to avoid overloading the headnode).  Format will be 'long':
bsub
cmo_fillout
-m $maf
-o ${maf}.fillout
-g GRCh37
-f 1
-v default
-b $bamList


# Use R for transforming this table:
library(reshape2)
fillout_long <- read.table("${maf}.fillout", header=1, sep="\t", quote="")

# Calculate the variant allele fractions; note: there are zeros.
fillout_long$t_VAF <- fillout_long$t_alt_count / fillout_long$t_total_count

# Styled genotype reporting
fillout_long$genotype <- paste(round(fillout_long$t_VAF, digits=5), " (", fillout_long$t_alt_count, "/", fillout_long$t_total_count, ")", sep="")

# Create a lookup key for the future merge back into and extend the maf; chr ^ start_pos ^ end_pos ^ ref ^ alt
fillout_long$lookupKey <- paste(fillout_long$Chromosome, "^", fillout_long$Start_Position, "^", fillout_long$End_Position, "^", fillout_long$Reference_Allele, "^", fillout_long$Tumor_Seq_Allele1, sep="")

fillout_stripped_long <- fillout_long[,c("lookupKey", "Tumor_Sample_Barcode", "genotype")]

fillout_stripped_wide <- dcast(fillout_stripped_long, lookupKey ~ Tumor_Sample_Barcode)


# Now merge this, using the lookup key or other key of your choice, onto the end of the maf and filter down to one row per unique mutation.  This will aid in analysis and reporting.
