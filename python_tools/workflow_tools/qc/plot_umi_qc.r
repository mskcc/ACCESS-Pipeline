#! /usr/bin/env Rscript

# load the libraries
library(ggplot2)
library(dplyr)
library(grid)
library(gridExtra)
library(scales)s

options(show.error.locations = TRUE)
options(error=quote({dump.frames(to.file=TRUE); q()}))
options(error=function()traceback(2))


argv = commandArgs(trailingOnly=TRUE)
# cluster_sizes --> "cluster-sizes.txt"
# cluster_sizes_post_filtering --> "cluster-sizes-post-filtering.txt"
# clusters_per_position --> "clusters-per-position.txt"
# clusters_per_position_post_filtering --> "clusters-per-position-post-filtering.txt"


# Util for putting commas in scale labels?
format_comma <- function(x, ...) {
  format(x, ..., big.mark = ',', scientific = FALSE, trim = TRUE)
}


# To plot cluster size (family size)
plot_cluster_size = function(table_path) {
  clusters = read.table(table_path, sep = "\t", header = TRUE, colClasses = c("numeric", "character"))
  clusters$Sample = factor(clusters$Sample)
  clusters = clusters %>% mutate(Sample = gsub('_IGO.*', '', Sample))
  clusters = clusters %>% mutate(Sample = gsub('-IGO.*', '', Sample))
  
  ggplot(clusters, aes(ClusterSize)) + 
    geom_freqpoly(binwidth=1, aes(color=Sample)) + 
    ylab("Frequency") + 
    coord_cartesian(xlim = c(0, 30)) +
    scale_y_continuous(label=format_comma) +
    scale_x_continuous('Family Size')
  
  ggsave("cluster-sizes.pdf", width=8, height=5)
}


# To Plot cluster size (post filtering)
plot_cluster_size_post_filtering = function(table_path) {
  clusters = read.table(table_path, sep = "\t", header = TRUE, colClasses = c("numeric", "character"))
  clusters$Sample = factor(clusters$Sample)
  clusters = clusters %>% mutate(Sample = gsub('_IGO.*', '', Sample))
  clusters = clusters %>% mutate(Sample = gsub('-IGO.*', '', Sample))
  ggplot(clusters, aes(ClusterSize)) + 
    geom_freqpoly(binwidth=1, aes(color=Sample)) + 
    ylab("Frequency") + 
    coord_cartesian(xlim = c(0, 30)) + 
    scale_x_continuous('Family Size') +
    scale_y_continuous(label=format_comma)
  
  ggsave("cluster-sizes-post-filtering.pdf", width=8, height=5)
}


# To plot clusters per position
plot_clusters_per_position = function(table_path) {
  clusters = read.table(table_path, sep = "\t", header = TRUE, colClasses = c("numeric", "character"))
  clusters$Sample = factor(clusters$Sample)
  clusters = clusters %>% mutate(Sample = gsub('_IGO.*', '', Sample))
  clusters = clusters %>% mutate(Sample = gsub('-IGO.*', '', Sample))
  
  ggplot(clusters, aes(Clusters)) + 
    geom_freqpoly(binwidth=1, aes(color=Sample)) + 
    ylab("Frequency") + 
    coord_cartesian(xlim = c(0, 30)) +
    scale_y_continuous(label=format_comma) + 
    scale_x_continuous('Families per Position')
  
  ggsave("clusters-per-position.pdf", width=8, height=5)
}


# To plot clusters per position (post filtering)
plot_clusters_per_position_post_filtering = function(table_path) {
  clusters = read.table(table_path, sep = "\t", header = TRUE, colClasses = c("numeric", "character"))
  clusters$Sample = factor(clusters$Sample)
  clusters = clusters %>% mutate(Sample = gsub('_IGO.*', '', Sample))
  clusters = clusters %>% mutate(Sample = gsub('-IGO.*', '', Sample))
  
  ggplot(clusters, aes(Clusters)) + geom_freqpoly(binwidth=1, aes(color=Sample)) + 
    ylab("Frequency") + 
    coord_cartesian(xlim = c(0, 30)) +
    scale_y_continuous(label=format_comma)
  
  ggsave("clusters-per-position-post-filtering.pdf", width=8, height=5)
}


# To plot family types, A & B Targets
plot_family_types = function(family_types_A_filepath, family_types_B_filepath) {
  # a = '~/Downloads/umi_qc_test/family-types-A.txt'
  family_types_A = read.table(family_types_A_filepath, sep = "\t", header = TRUE, colClasses = c('character', 'character', 'numeric'))
  family_types_A$Count = as.numeric(family_types_A$Count)
  family_types_A$Pool = 'A Targets'
  
  # b = '~/Downloads/umi_qc_test/family-types-B.txt'
  family_types_B = read.table(family_types_B_filepath, sep = "\t", header = TRUE, colClasses = c('character', 'character', 'numeric'))
  family_types_B$Count = as.numeric(family_types_B$Count)
  family_types_B$Pool = 'B Targets'
  
  family_types_all = bind_rows(family_types_A, family_types_B)
  
  family_types_all[is.na(family_types_all)] <- 0
  family_types_all = family_types_all %>% mutate(Sample = gsub('_IGO.*', '', Sample))
  family_types_all = family_types_all %>% mutate(Sample = gsub('-IGO.*', '', Sample))
  family_types_all$Sample = factor(family_types_all$Sample)
  family_types_all$Type = factor(family_types_all$Type, levels=c('Singletons', 'Sub-Simplex', 'Simplex', 'Duplex'))
  
  # Convert to % family sizes
  family_types_all = family_types_all %>%
    group_by(Pool, Sample) %>%
    mutate(CountPercent = Count / sum(Count))
  
  ggplot(family_types_all, aes(x=Sample, y=CountPercent)) +
      geom_bar(position=position_stack(reverse=TRUE), stat='identity', aes(fill=Type)) + 
      facet_grid(Pool ~ ., scales='free') +
      scale_y_continuous('Read Count', labels = percent_format())
  
  ggsave('family-types.pdf', width=8, height=5)
}


plot_cluster_size(argv[1])
plot_cluster_size_post_filtering(argv[2])
plot_clusters_per_position(argv[3])
plot_clusters_per_position_post_filtering(argv[4])
plot_family_types(argv[5], argv[6])

warnings()
