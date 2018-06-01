#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

# load the libraries
library(ggplot2)
library(dplyr)
library(grid)
library(gridExtra)


# Sample	GenotypeCount	AltCount	AltPercent	ContributingSites	Method
# BL-tdm1-005-pl-T02-30ng-a_IGO_05500_ET_41_S41_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	3338084410	3654122	0.109348	220426	Total
# BL-tdm1-005-pl-T02-30ng-a_IGO_05500_ET_41_S41_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	643209654	406085	0.0630943	165854	Unique
# BL-tdm1-005-pl-T02-30ng_IGO_05500_ET_66_S66_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	4143848064	5505763	0.13269	222475	Total
# BL-tdm1-005-pl-T02-30ng_IGO_05500_ET_66_S66_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	668902987	440716	0.065843	173373	Unique
# BL-tdm1-012-pl-T02-30ng-a_IGO_05500_ET_39_S39_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	5096543543	5733208	0.112366	221462	Total
# BL-tdm1-012-pl-T02-30ng-a_IGO_05500_ET_39_S39_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	879601578	572640	0.0650598	176675	Unique
# BL-tdm1-012-pl-T02-30ng_IGO_05500_ET_64_S64_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	6309070603	8567249	0.135608	223484	Total
# BL-tdm1-012-pl-T02-30ng_IGO_05500_ET_64_S64_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	917423319	620477	0.0675869	183712	Unique
# BL-tdm1-020-pl-T02-30ng-a_IGO_05500_ET_40_S40_001_cl_aln_srt_MD_IR_FX_BR-pileup.txt	4072777190	4315557	0.105849	222075	Total


# To plot noise
noise = read.table(args[1], sep = "\t", header = TRUE, colClasses = c("character", "numeric", "numeric", "numeric", "numeric", "character"))
noise$Sample = factor(noise$Sample)

noise = noise %>% mutate(Sample = gsub('_IGO.*', '', Sample))
noise = noise %>% mutate(Sample = gsub('-IGO.*', '', Sample))

ggplot(noise, aes(AltPercent)) + geom_freqpoly(binwidth=1, aes(color=Sample)) + ylab("Noise (%)") #+ coord_cartesian(xlim = c(0, 30))
ggsave("noise.pdf", width=8, height=5)

ggplot(noise, aes(ContributingSites)) + geom_freqpoly(binwidth=1, aes(color=Sample)) + ylab("Contributing Sites") #+ coord_cartesian(xlim = c(0, 30))
ggsave("contributing_sites.pdf", width=8, height=5)

warnings()
