#! /usr/bin/env Rscript

# load the libraries
library(ggplot2)
library(dplyr)
library(grid)
library(gridExtra)


# Util for putting commas in scale labels
format_comma <- function(x, ...) {
  format(x, ..., big.mark = ',', scientific = FALSE, trim = TRUE)
}

# Todo: merge with plotting-collapsed-bams.r
cleanup_sample_names_2 = function(data) {
  data = data %>% mutate(Sample = gsub('_md', '', Sample))
  data = data %>% mutate(Sample = gsub('-md', '', Sample))
  data = data %>% mutate(Sample = gsub('.bam', '', Sample))
  data = data %>% mutate(Sample = gsub('Sample_', '', Sample))
  data = data %>% mutate(Sample = gsub('Sample-', '', Sample))
  data = data %>% mutate(Sample = gsub('Sample', '', Sample))
  data = data %>% mutate(Sample = gsub('_IGO.*', '', Sample))
  data = data %>% mutate(Sample = gsub('-IGO.*', '', Sample))
  data = data %>% mutate(Sample = gsub('_bc.*', '', Sample))
  
  # Ex: ZS-msi-4506-pl-T01_IGO_05500_EF_41_S41_standard...
  data = data %>% mutate(Sample = gsub('_standard.*', '', Sample))
  
  # Ex: ZS-msi-4506-pl-T01_IGO_05500_EF_41_S41
  #                                       ^^^^
  data = data %>% mutate(Sample = gsub('_.\\d\\d$', '', Sample))
  data
}

# To plot family sizes
families = read.table('family-sizes.txt', sep = '\t', header = TRUE, colClasses = c('numeric', 'character', 'numeric', 'character'))
families$Sample = factor(families$Sample)
families = cleanup_sample_names_2(families)

ggplot(filter(families, FamilyType=='All'), aes(FamilySize, Frequency, color=Sample)) + 
  geom_point() + 
  geom_line() + 
  ggtitle('All Unique Family Sizes') +
  xlab('Family Size') + 
  scale_y_continuous('Frequency', label=format_comma) +
  coord_cartesian(xlim = c(0, 40))

ggplot(filter(families, FamilyType=='Simplex'), aes(FamilySize, Frequency, color=Sample)) + 
  geom_point() + 
  geom_line() + 
  ggtitle('Simplex Family Sizes') +
  xlab('Family Size') + 
  scale_y_continuous('Frequency', label=format_comma) +
  coord_cartesian(xlim = c(0, 40))

ggplot(filter(families, FamilyType=='Duplex'), aes(FamilySize, Frequency, color=Sample)) + 
  geom_point() + 
  geom_line() + 
  ggtitle('Duplex Family Sizes') +
  xlab('Family Size') + 
  scale_y_continuous('Frequency', label=format_comma) +
  coord_cartesian(xlim = c(0, 40))
