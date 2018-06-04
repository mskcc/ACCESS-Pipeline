#! /usr/bin/env Rscript

# load the libraries
library(ggplot2)
library(dplyr)
library(grid)
library(gridExtra)


argv = commandArgs(trailingOnly=TRUE)
# cluster_sizes --> "cluster-sizes.txt"
# cluster_sizes_post_filtering --> "cluster-sizes-post-filtering.txt"
# clusters_per_position --> "clusters-per-position.txt"
# clusters_per_position_post_filtering --> "clusters-per-position-post-filtering.txt"


# to plot cluster size (family size)
clusters = read.table(argv[1], sep = "\t", header = TRUE, colClasses = c("numeric", "character"))
clusters$Sample = factor(clusters$Sample)
clusters = clusters %>% mutate(Sample = gsub('_IGO.*', '', Sample))
clusters = clusters %>% mutate(Sample = gsub('-IGO.*', '', Sample))
ggplot(clusters, aes(ClusterSize)) + geom_freqpoly(binwidth=1, aes(color=Sample)) + ylab("Frequency") + coord_cartesian(xlim = c(0, 30))
ggsave("cluster-sizes.pdf", width=8, height=5)

clusters = read.table(argv[2], sep = "\t", header = TRUE, colClasses = c("numeric", "character"))
clusters$Sample = factor(clusters$Sample)
clusters = clusters %>% mutate(Sample = gsub('_IGO.*', '', Sample))
clusters = clusters %>% mutate(Sample = gsub('-IGO.*', '', Sample))
ggplot(clusters, aes(ClusterSize)) + geom_freqpoly(binwidth=1, aes(color=Sample)) + ylab("Frequency") + coord_cartesian(xlim = c(0, 30))
ggsave("cluster-sizes-post-filtering.pdf", width=8, height=5)

# to plot clusters per position
clusters = read.table(argv[3], sep = "\t", header = TRUE, colClasses = c("numeric", "character"))
clusters$Sample = factor(clusters$Sample)
clusters = clusters %>% mutate(Sample = gsub('_IGO.*', '', Sample))
clusters = clusters %>% mutate(Sample = gsub('-IGO.*', '', Sample))
ggplot(clusters, aes(Clusters)) + geom_freqpoly(binwidth=1, aes(color=Sample)) + ylab("Frequency") + coord_cartesian(xlim = c(0, 30))
ggsave("clusters-per-position.pdf", width=8, height=5)

clusters = read.table(argv[4], sep = "\t", header = TRUE, colClasses = c("numeric", "character"))
clusters$Sample = factor(clusters$Sample)
clusters = clusters %>% mutate(Sample = gsub('_IGO.*', '', Sample))
clusters = clusters %>% mutate(Sample = gsub('-IGO.*', '', Sample))
ggplot(clusters, aes(Clusters)) + geom_freqpoly(binwidth=1, aes(color=Sample)) + ylab("Frequency") + coord_cartesian(xlim = c(0, 30))
ggsave("clusters-per-position-post-filtering.pdf", width=8, height=5)


warnings()
