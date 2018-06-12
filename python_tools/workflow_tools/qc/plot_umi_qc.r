#! /usr/bin/env Rscript

# load the libraries
library(ggplot2)
library(dplyr)
library(grid)
library(gridExtra)
library(scales)


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
  data
}

# % Family Types Graph
family_types_A = read.table('family-types-A.txt', sep = "\t", header = TRUE, colClasses = c('character', 'character', 'numeric'))
family_types_A$Count = as.numeric(family_types_A$Count)
family_types_A$Pool = 'A Targets'

family_types_B = read.table('family-types-B.txt', sep = "\t", header = TRUE, colClasses = c('character', 'character', 'numeric'))
family_types_B$Count = as.numeric(family_types_B$Count)
family_types_B$Pool = 'B Targets'
family_types_all = bind_rows(family_types_A, family_types_B)
family_types_all[is.na(family_types_all)] <- 0

family_types_all$Sample = factor(family_types_all$Sample)
family_types_all$Type = factor(family_types_all$Type, levels=c('Duplex', 'Simplex', 'Sub-Simplex', 'Singletons'))
family_types_all = family_types_all %>% mutate(Sample = gsub('_IGO.*', '', Sample))
family_types_all = family_types_all %>% mutate(Sample = gsub('-IGO.*', '', Sample))
family_types_all = cleanup_sample_names_2(family_types_all)

# Convert to % family sizes
family_types_all = family_types_all %>%
  group_by(Pool, Sample) %>%
  mutate(CountPercent = Count / sum(Count))

ggplot(family_types_all, aes(x=Sample, y=CountPercent)) +
    geom_bar(position=position_stack(reverse=TRUE), stat='identity', aes(fill=Type)) + 
    facet_grid(Pool ~ ., scales='free') +
    scale_y_continuous('Read Count', labels = percent_format()) +
    theme(axis.text.x = element_text(angle = 90, hjust = 1))

# To plot family sizes
families = read.table('family-sizes.txt', sep = '\t', header = TRUE, colClasses = c('numeric', 'character', 'numeric', 'character'))
families$Sample = factor(families$Sample)
families = cleanup_sample_names_2(families)

ggplot(filter(families, FamilyType=='All'), aes(FamilySize, Frequency, color=Sample)) + 
  geom_point(size=1) + 
  geom_line() + 
  ggtitle('All Unique Family Sizes') +
  xlab('Family Size') + 
  scale_y_continuous('Frequency', label=format_comma) +
  coord_cartesian(xlim = c(0, 40))

ggplot(filter(families, FamilyType=='Simplex'), aes(FamilySize, Frequency, color=Sample)) + 
  geom_point(size=1) + 
  geom_line() + 
  ggtitle('Simplex Family Sizes') +
  xlab('Family Size') + 
  scale_y_continuous('Frequency', label=format_comma) +
  coord_cartesian(xlim = c(0, 40))

ggplot(filter(families, FamilyType=='Duplex'), aes(FamilySize, Frequency, color=Sample)) + 
  geom_point(size=1) + 
  geom_line() + 
  ggtitle('Duplex Family Sizes') +
  xlab('Family Size') + 
  scale_y_continuous('Frequency', label=format_comma) +
  coord_cartesian(xlim = c(0, 40))
