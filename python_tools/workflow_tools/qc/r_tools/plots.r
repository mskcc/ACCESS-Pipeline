##################################################
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# Maintainer: Ian Johnson (johnsoni@mskcc.org)
##################################################

library(grid)
library(yaml)
library(tidyr)
library(scales)
library(gridBase)
library(gridExtra)
library(lattice)
library(ggplot2)
library(reshape2)
library(data.table)
library(wesanderson)
suppressMessages(library(dplyr))

# Source constants
source_local('constants.r')

#' Count of read pairs per sample
#' @param data data.frame with Sample and total_reads columns
plot_read_pairs_count = function(data) {
  data = data %>% mutate(read_pairs = TotalReads / 2)
  # Because the values for read counts are the same for both Pool A and Pool B, we just pick one
  data = filter(data, pool == 'A Targets')
  
  g = ggplot(data, aes_string(x = SAMPLE_ID_COLUMN, y = 'read_pairs')) + 
    geom_bar(stat='identity') + 
    ggtitle('Read Pairs') +
    scale_y_continuous('Count', label=format_comma) +
    scale_fill_manual(values=c(MSK_ORANGE)) +
    MAIN_PLOT_THEME
  
  ggsave(g, file='read_counts.pdf', width=20, height=8.5)
}


#' Function to plot number of reads that aligned to the reference genome
#' @param data data.frame with the usual columns
plot_align_genome = function(data) {
  data$AlignFrac = as.numeric(data$AlignFrac)
  class_count = length(unique(data[[TITLE_FILE__SAMPLE_CLASS_COLUMN]]))
  class_col_palette = (grDevices::colorRampPalette(wes_palettes[[CONTINUOUS_COLOR_PALETTE]]))(class_count)
  g = ggplot(data, aes_string(x = SAMPLE_ID_COLUMN, y = 'AlignFrac')) +
    geom_bar(position='dodge', stat='identity', aes_string(fill = TITLE_FILE__SAMPLE_CLASS_COLUMN)) +
    ggtitle('Fraction of Total Reads that Align to the Human Genome') +
    scale_y_continuous('Fraction of Reads', label=format_comma) + 
    coord_cartesian(ylim=c(0.8, 1)) +
    scale_fill_manual(values=class_col_palette) +
    MAIN_PLOT_THEME
  
  ggsave(g, file='align_rate.pdf', width=20, height=8.5)
}



#' Plot on bait rate
#' (usually a metric for standard bams)
#' @param data data.frame with the usual columns
plot_on_bait = function(data) {
  g = ggplot(data, aes_string(x = SAMPLE_ID_COLUMN, y = 'TotalOnTargetFraction')) +
    geom_bar(position = position_stack(reverse = TRUE), stat='identity', aes(fill = pool)) +
    ggtitle('Fraction of On Bait Reads') +
    scale_y_continuous('Fraction of Reads', label=format_comma, limits=c(0,1)) +
    scale_fill_manual(values=c(MSK_BLUE, MSK_ORANGE)) +
    MAIN_PLOT_THEME
  
  ggsave(g, file='on_target_rate.pdf', width=11, height=8.5)
}


#' Plot Coverage vs %GC content, separately for each sample
#' (for each collapsing method)
#' @param data data.frame with the usual columns
plot_gc_with_cov_each_sample = function(data) {
  data = data[complete.cases(data[, 'coverage']),]
  sample_count = dim(unique(data[SAMPLE_ID_COLUMN]))[1]

  # Only plot for Total and All Unique
  gc_bias_levels = c('TotalCoverage', 'All Unique')
  data = dplyr::filter(data, method %in% gc_bias_levels)
  data = mutate(data, method = factor(method, levels=gc_bias_levels))
  data = mutate(data, !!SAMPLE_ID_COLUMN := factor(!!data[,SAMPLE_ID_COLUMN]))
  
  g = ggplot(data, aes_string(x = 'gc_bin', y = 'coverage', group = SAMPLE_ID_COLUMN, color = SAMPLE_ID_COLUMN)) +
    geom_line() +
    facet_grid(method ~ ., scales='free') +
    ggtitle('Average Coverage versus GC bias (Pool A Targets)') +
    scale_y_continuous('Average Coverage', label = format_comma, limits = c(0, NA)) +
    xlab('GC Bias') +
    MAIN_PLOT_THEME +
    scale_colour_manual(values = (grDevices::colorRampPalette(wes_palettes[[CONTINUOUS_COLOR_PALETTE]]))(sample_count))
  
  ggsave(g, file='gc_cov_each_sample.pdf', width=11, height=8.5)
}


#' Plot the distribution of insert sizes (a.k.a. fragment lengths),
#' as well as most frequent insert sizes
#' @param insertSizes data.frame of Sample, FragmentSize, TotalFrequency, UniqueFrequency
plot_insert_size_distribution = function(insert_sizes) {
  
  insert_sizes = insert_sizes %>%
    group_by_(SAMPLE_ID_COLUMN) %>%
    mutate(total_frequency_fraction = TotalFrequency / sum(TotalFrequency)) %>%
    ungroup()
  
  peaks = insert_sizes %>% 
    group_by_(SAMPLE_ID_COLUMN) %>%
    filter(TotalFrequency == max(TotalFrequency)) %>%
    filter(FragmentSize == max(FragmentSize))
  
  peaks = peaks %>%
    rename(peak = TotalFrequency, peak_insert_size = FragmentSize)
  # Only need these columns from peaks table
  peaks = peaks[, c('peak', 'peak_insert_size', SAMPLE_ID_COLUMN)]
  
  # Put peak alongside Sample ID in legend
  insert_sizes = insert_sizes %>%
    inner_join(peaks, by = paste(SAMPLE_ID_COLUMN))
  
  insert_sizes$sample_and_peak = paste(
    insert_sizes[[SAMPLE_ID_COLUMN]],
    insert_sizes$peak_insert_size,
    sep=', '
  )

  # Group control samples with test samples
  insert_sizes[(insert_sizes[TITLE_FILE__SAMPLE_CLASS_COLUMN] == POOLTUMOR | insert_sizes[TITLE_FILE__SAMPLE_CLASS_COLUMN] == POOLNORMAL), TITLE_FILE__SAMPLE_CLASS_COLUMN] = TUMOR
 
  # get sample count to get colour palette for continuous variables
  sample_count = dim(unique(insert_sizes[SAMPLE_ID_COLUMN]))[1]
  g = ggplot(insert_sizes, aes(x = FragmentSize, y = total_frequency_fraction, colour = sample_and_peak)) +
    facet_grid(Class ~ ., labeller = as_labeller(c("Tumor" = "Tumor & Control", "Normal" = "Normal"))) +
    geom_line(size = 0.5) +
    ggtitle('Insert Size Distribution (from All Unique reads, Pool A)') +
    xlab('Insert Size') +
    ylab('Frequency (%)') +
    labs(colour = 'Sample, Peak Insert Size') +
    theme(legend.position = c(.75, .5)) +
    scale_colour_manual(values = (grDevices::colorRampPalette(wes_palettes[[CONTINUOUS_COLOR_PALETTE]]))(sample_count)) +
    MAIN_PLOT_THEME
  
  ggsave(g, file='insert_sizes.pdf', width=11, height=8.5)
}


#' Distribution of coverage across targets (total and unique)
#' Function to plot histogram of coverage per target interval distribution
#' Coverage values are scaled by the mean of the distribution
#' @param data data.frame with Sample ID, and coverage columns (one entry for each interval)
plot_cov_dist_per_interval_line = function(data) {
  data = data %>%
    group_by_(SAMPLE_ID_COLUMN) %>%
    mutate(coverage_scaled = peak_coverage / median(peak_coverage))
  
  # Group control samples with test samples
  data[(data[TITLE_FILE__SAMPLE_CLASS_COLUMN] == POOLTUMOR | data[TITLE_FILE__SAMPLE_CLASS_COLUMN] == POOLNORMAL), TITLE_FILE__SAMPLE_CLASS_COLUMN] = TUMOR
 
  # get sample count to get colour palette for continuous variables
  sample_count = dim(unique(data[SAMPLE_ID_COLUMN]))[1] 
  g = ggplot(data) +
    geom_line(aes_string(x = 'coverage_scaled', colour = SAMPLE_ID_COLUMN), stat='density') +
    facet_grid(Class ~ ., labeller = as_labeller(c("Tumor" = "Tumor & Control", "Normal" = "Normal"))) +
    ggtitle('Distribution of Coverages per Probe Interval (from all unique reads, A Targets)') +
    scale_y_continuous('Frequency', label=format_comma) +
    scale_x_continuous('Coverage (median scaled)') + 
    coord_cartesian(xlim=c(0, 2)) +
    theme(legend.position = c(.75, .5)) +
    scale_colour_manual(values = (grDevices::colorRampPalette(wes_palettes[[CONTINUOUS_COLOR_PALETTE]]))(sample_count)) +
    MAIN_PLOT_THEME
  
  ggsave(g, file='coverage_per_interval.pdf', width=11, height=8.5)
}


#' Average coverage for Exon-level Targets (as opposed to baits)
#' @param data data.frame with Sample ID and average_coverage columns.
#' For ACCESS, this will be plotted from duplex reads, A Targets
plot_average_target_coverage = function(data) {
  pdf(file = 'average_coverage_duplex_A_exon.pdf', width=11, height=8, onefile=TRUE)
  
  avg_cov_df = data %>% 
    group_by_(TITLE_FILE__SAMPLE_CLASS_COLUMN) %>%
    summarise_at(vars(TotalCoverage), funs(mean(., na.rm=TRUE)))
  
  # TotalCoverage column from aggregate bam metrics script is actually duplex in this case
  avg_cov_df = avg_cov_df %>%
    rename(DuplexCoverage = TotalCoverage)
  
  # Round to one decimal place
  avg_cov_df$DuplexCoverage = round(avg_cov_df$DuplexCoverage, 1)
  
  g = ggplot(data, aes_string(x = SAMPLE_ID_COLUMN, y = 'TotalCoverage')) +
    geom_bar(stat = 'identity') +
    ggtitle('Average Coverage across Target Exons (from duplex reads, A Targets)') +
    scale_y_continuous('Average Coverage', label = format_comma) +
    scale_fill_manual(values = c(MSK_ORANGE)) +
    MAIN_PLOT_THEME
  
  # Print table and plot
  table_theme = ttheme_default(base_size=12)
  avg_cov_tbl = tableGrob(avg_cov_df, theme=table_theme, rows=NULL)
  
  layout(matrix(c(1,2,2,2), nrow=4, ncol=2, byrow=TRUE))
  par(mfrow=c(2, 1))
  grob_list = list(avg_cov_tbl, g)
  grid.arrange(grobs = grob_list, nrow=2, as.table=FALSE, heights=c(1, 3))
  dev.off()
}


#' Plot three things:
#' 1. Table of average coverages for Plasma / Buffy Coat samples
#' 2. Mean Coverage values per sample, for each collapsing type
#' 3. % Family Types plot for each collapsed sample
plot_mean_cov_and_family_types = function(coverage_data, family_types_data, pool_name, file_prefix) {
  pdf(file = paste(file_prefix, '_cov_and_family_types.pdf', sep=''), height=20, width=8.5, onefile=TRUE)
  
  coverage_data = coverage_data %>% filter(pool == pool_name)
  
  
  #******* COVERAGE TABLE ********#
  # Include a table of average coverage values across samples
  avg_cov_df = coverage_data %>%
    group_by_(TITLE_FILE__SAMPLE_CLASS_COLUMN, 'pool', 'method') %>%
    summarise_at(vars(average_coverage), funs(mean(., na.rm=TRUE)))
  
  # Round to one decimal place
  avg_cov_df$average_coverage = round(avg_cov_df$average_coverage, 1)
  
  avg_cov_df = dcast(
    avg_cov_df,
    as.formula(paste(TITLE_FILE__SAMPLE_CLASS_COLUMN, '+ pool ~ method')),
    value.var='average_coverage'
  )
  
  
  #******* COVERAGE PLOT ********#
  LEVEL_C = c('TotalCoverage', 'All Unique', 'Simplex', 'Duplex')
  data = filter(coverage_data, method %in% LEVEL_C)
  data = transform(data, method=factor(method, levels=LEVEL_C))
  data = transform(data, pool=factor(pool, levels=c('A Targets', 'B Targets')))
  
  full_coverage_df = data %>% data.table() %>%
    # Convert collapsing method column to columns for each collapsing type
    spread(key = method, value = average_coverage) %>% 
    # For each sample and pool,
    group_by_(SAMPLE_ID_COLUMN, 'pool') %>% 
    # Create a new colum for the Sub Simplex + Singletons coverage
    mutate('Sub Simplex + Singletons' = `All Unique` - (Duplex + Simplex)) %>% 
    # Grab just these new columns, along with Sample and pool
    select(!!SAMPLE_ID_COLUMN, 'pool', 'TotalCoverage', 'Sub Simplex + Singletons', 'Simplex', 'Duplex', 'All Unique') %>%
    # Convert collapsing method types back to single column
    melt(id = c(SAMPLE_ID_COLUMN, 'pool')) %>%
    # Rename it to average_coverage
    rename(method=variable, average_coverage=value)
  
  # No need for All Unique values
  desired_levels = c('TotalCoverage', 'Sub Simplex + Singletons', 'Simplex', 'Duplex')
  full_coverage_df = filter(full_coverage_df, method %in% desired_levels)
  # Ensure proper plotting sort order
  full_coverage_df = transform(full_coverage_df, method=factor(method, levels=desired_levels))
  
  # New variable for faceting on collapsed vs uncollapsed coverage
  full_coverage_df$total_or_collapsed = factor(
    ifelse(full_coverage_df$method == 'TotalCoverage', 'Total', 'Collapsed'),
    levels=c('Total', 'Collapsed'))
  full_coverage_df = full_coverage_df %>% arrange(total_or_collapsed, method)
  
  avg_coverage_plot = ggplot(full_coverage_df, aes_string(x = SAMPLE_ID_COLUMN, y = 'average_coverage')) +
    facet_grid(total_or_collapsed ~ . , scales='free') +
    geom_bar(position = 'stack', stat = 'identity', aes(fill = method)) +
    ggtitle('Average Coverage per Sample') +
    scale_y_continuous('Average Coverage', label = format_comma) +
    scale_fill_manual(values=c(MSK_GREY, MSK_LIGHT_BLUE, MSK_BLUE, MSK_ORANGE)) +
    MAIN_PLOT_THEME
  
  
  #******* FAMILY TYPES PLOT ********#
  # family_types_data$Count = as.numeric(family_types_data$Count)
  
  # family_types_data[is.na(family_types_data)] <- 0
  
  family_types_data$Type = factor(
    family_types_data$Type, 
    levels=c('Duplex', 'Simplex', 'Sub-Simplex', 'Singletons')
  )
  
  family_types_data$Pool = pool_name
  
  # Convert to % family sizes
  family_types_data = family_types_data %>%
    group_by_(SAMPLE_ID_COLUMN, 'Pool') %>%
    mutate(CountPercent = Count / sum(Count)) %>%
    ungroup()
  
  # family_types_data[is.na(family_types_data)] <- 0
  
  # Sort again by class after groupBy
  family_types_data[[SAMPLE_ID_COLUMN]] = factor(
    family_types_data[[SAMPLE_ID_COLUMN]],
    levels = unique(unlist(family_types_data[[SAMPLE_ID_COLUMN]]))
  )
  
  family_types_plot = ggplot(family_types_data, aes_string(x = SAMPLE_ID_COLUMN, y = 'CountPercent')) +
    geom_bar(position = position_fill(reverse = TRUE), stat = 'identity', aes(fill = Type)) +
    scale_y_continuous('UMI Family Proportion', labels = percent_format()) +
    scale_fill_manual(values=c(MSK_ORANGE, MSK_BLUE, MSK_LIGHT_BLUE, MSK_GREY)) +
    guides(fill = guide_legend(reverse = TRUE)) +
    MAIN_PLOT_THEME
  
  #******* PRINT GROBS *********#
  table_theme = ttheme_default(base_size=12)
  title_grob = textGrob(pool_name, gp = gpar(fontsize = 16))
  avg_cov_tbl = tableGrob(avg_cov_df, theme=table_theme, rows=NULL)
  
  layout(matrix(c(1,2,3,3,3,4,4,4), nrow=8, ncol=2, byrow=TRUE))
  par(mfrow=c(4, 1))
  
  grob_list = list(title_grob, avg_cov_tbl, avg_coverage_plot, family_types_plot)
  grid.arrange(grobs = grob_list, nrow=4, as.table=FALSE, heights=c(1, 2, 9, 9))
  dev.off()
}


#' Family sizes curves
#' @param data data.frame with Sample, FamilySize, and Frequency columns
plot_family_curves <- function(data) {
  data[, SAMPLE_ID_COLUMN] = factor(data[, SAMPLE_ID_COLUMN])
  # Only plot the Plasma samples
  data = data[data[TITLE_FILE__SAMPLE_TYPE_COLUMN] == 'Plasma',]
  sample_count = dim(unique(data[SAMPLE_ID_COLUMN]))[1]
  
  g = ggplot(
    filter(data, FamilyType=='All'),
    aes_string('FamilySize', 'Frequency', color = SAMPLE_ID_COLUMN)) +
    geom_point(size=.5) +
    geom_line() +
    ggtitle('All Unique Family Sizes') +
    xlab('Family Size') +
    scale_y_continuous('Frequency', label = format_comma) +
    coord_cartesian(xlim = c(0, 40)) +
    MAIN_PLOT_THEME +
    scale_colour_manual(values = (grDevices::colorRampPalette(wes_palettes[[CONTINUOUS_COLOR_PALETTE]]))(sample_count))
  ggsave(g, file='family_sizes_all.pdf', width = 11, height = 8.5)
  
  g = ggplot(
    filter(data, FamilyType=='Simplex'),
    aes_string('FamilySize', 'Frequency', color = SAMPLE_ID_COLUMN)) + 
    geom_point(size=.5) + 
    geom_line() + 
    ggtitle('Simplex Family Sizes') +
    xlab('Family Size') + 
    scale_y_continuous('Frequency', label = format_comma) +
    coord_cartesian(xlim = c(0, 40)) +
    MAIN_PLOT_THEME +
    scale_colour_manual(values = (grDevices::colorRampPalette(wes_palettes[[CONTINUOUS_COLOR_PALETTE]]))(sample_count))
  ggsave(g, file='family_sizes_simplex.pdf', width = 11, height = 8.5)
  
  g = ggplot(
    filter(data, FamilyType=='Duplex'),
    aes_string('FamilySize', 'Frequency', color = SAMPLE_ID_COLUMN)) + 
    geom_point(size=.5) + 
    geom_line() + 
    ggtitle('Duplex Family Sizes') +
    xlab('Family Size') + 
    scale_y_continuous('Frequency', label=format_comma) +
    coord_cartesian(xlim = c(0, 40)) +
    MAIN_PLOT_THEME + 
    scale_colour_manual(values = (grDevices::colorRampPalette(wes_palettes[[CONTINUOUS_COLOR_PALETTE]]))(sample_count))
  ggsave(g, file='family_sizes_duplex.pdf', width = 11, height = 8.5)
}
