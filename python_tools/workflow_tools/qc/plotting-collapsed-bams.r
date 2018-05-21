#! /usr/bin/env Rscript

##################################################
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# Maintainer: Ian Johnson (johnsoni@mskcc.org)
##################################################

library(grid)
library(lattice)
library(ggplot2)
library('getopt');
library(reshape2)
library(gridExtra)
suppressMessages(library(dplyr))
suppressMessages(library(ggrepel))


options(show.error.locations = TRUE)
options(error = quote({dump.frames(to.file=TRUE); q()}))
options(error=function()traceback(2))


# Util for putting commas in scale labels?
format_comma <- function(x, ...) {
  format(x, ..., big.mark = ',', scientific = FALSE, trim = TRUE)
}


# Define our global plots theme
MY_THEME = theme(text = element_text(size=8),
  axis.text.x = element_text(angle = 45, hjust = 1, face='bold'),
  plot.margin = unit(c(.1, .1, .1, 1), 'in'))

# Some title file columns will not be printed
DROP_COLS = c('Pool_input', 'Barcode_index')

# Optional distinctive color palette
#' @param n Number of distinct colors to be returned
#' @return List of distinct colors (hue, luminance, contrast)?
gg_color_hue <- function(n) {
  hues = seq(15, 375, length = n + 1)
  lums = seq(0, 100, length = n + 1)
  hcl(h = hues, l = 65, c = 100)[1:n]
}


#' Levels and sort order for collapsing methods
LEVEL_C = c(
  'total',
  'unique',
  'unfiltered',
  'simplex_duplex',
  'duplex'
)

#' Util function to sort data by arbitrary list
#' @param df The data.frame to be sorted 
#' @param sort_column String - column to sort on
#' @param sort_list Vector of strings ordered in desired sort order for @df
sort_df = function(df, sort_column, sort_list) {
  sort_list = unique(unlist(sort_list))
  sort_list = as.factor(sort_list)
  df[[sort_column]] <- factor(df[[sort_column]], levels=sort_list)
  df = df[order(df[[sort_column]]),]
  df[[sort_column]] <- factor(df[[sort_column]], levels=unique(as.character(df[[sort_column]])) )
  return(df)
}


#' Function to read inputs and obtain the previously created tables
#' @param args Arguments from argv
#' @return Parsed list of (
#'   tables_output_dir_location,
#'   standard_waltz_output_dir_location,
#'   output_dir_for_plots,
#'   title_file_path
#' )
readInputs = function(args) {
  spec = matrix(c(
    'standardWaltz', 'w', 1, 'character',
    'tablesOutputDir', 'i', 1, 'character',
    'plotsOutputDir', 'o', 1, 'character',
    'titleFilePath', 't', 2, 'character'
  ), byrow=TRUE, ncol=4);
  
  opts = getopt(spec);

  return(c(
    opts$tablesOutputDir,
    opts$standardWaltz,
    opts$plotsOutputDir,
    opts$titleFilePath)
  )
}


#' Function to plot duplication fraction (Standard Bams only)
#' @param data data.frame with the usual columns
plotDupFrac = function(data) {

  # Plot may be used across collapsing methods, or with T/N coloring for just total values
  data = transform(data, method=factor(method, levels=LEVEL_C))
  # data = data %>% filter(method == 'picard')
  # if('Class' %in% colnames(data)) {
  #   fill_var = 'Class'
  # } else {
  #   fill_var = 'method'
  # }
  
  ggplot(data, aes(x = Sample, y = as.numeric(duplication_rate))) +
    geom_bar(stat='identity', aes_string(fill = 'method'), position = 'dodge') +
    ggtitle('Duplication Rate per Sample') +
    scale_y_continuous('Duplication Rate', label=format_comma) +
    MY_THEME
}


#' Function to plot number of reads that aligned to the reference genome
#' @param data data.frame with the usual columns
plotAlignGenome = function(data) {
  if('Class' %in% colnames(data)) {
    fill_var = 'Class'
  } else {
    fill_var = 'Sample'
  }

  # Todo: is this 'on target' or 'aligned to human genome'?
  ggplot(data, aes(x=Sample, y=total_on_target_fraction)) +
    geom_bar(position = 'dodge', stat='identity', aes_string(fill = fill_var)) +
    ggtitle('Fraction of Total Reads that Align to the Human Genome') +
    scale_y_continuous('Fraction of Reads', label=format_comma, limits=c(0.8, 1.0)) +
    MY_THEME
}


#' Plot average coverage for each sample,
#' for each collapsing method
#' @param data data.frame with the usual columns
plotMeanCov = function(data) {
  data = transform(data, method=factor(method, levels=LEVEL_C))
  data = transform(data, pool=factor(pool, levels=c('pool_a', 'pool_b')))
  
  ggplot(data, aes(x=Sample, y=average_coverage)) +
    facet_grid(pool~ ., , scales = 'free') +
    geom_bar(position = 'dodge', stat='identity', aes_string(fill='method')) +
    
    ggtitle('Average Coverage per Sample') +
    scale_y_continuous('Average Coverage', label=format_comma) +
    MY_THEME
}


#' Plot on target rate 
#' (usually a metric for standard bams)
#' @param data data.frame with the usual columns
plotOnTarget = function(data) {
  method_c = c('Sample', 'total_on_target_fraction', 'pool')

  ggplot(data, aes(x = Sample, y = total_on_target_fraction)) +
    geom_bar(position = position_stack(reverse = TRUE), stat='identity', aes(fill = pool)) +
    ggtitle('Fraction of On Target Reads') +
    scale_y_continuous('Fraction of Reads', label=format_comma) +
    MY_THEME
}


#' Plot Coverage vs %GC content, averaged over all samples 
#' (for each collapsing method)
#' @param data data.frame with the usual columns
plotGCwithCovAllSamples = function(data) {
  data = transform(data, method=factor(method, levels=LEVEL_C))
  
  ggplot(data, aes(x = gc_bin, y = coverage, color = method, group = method)) +
    geom_line() +
    ggtitle('Average Coverage versus GC bias') +
    scale_y_continuous('Average Coverage (all samples)', label=format_comma) +
    xlab('GC bias') +
    MY_THEME
}


#' Plot Coverage vs %GC content, separately for each sample 
#' (for each collapsing method)
#' @param data data.frame with the usual columns
plotGCwithCovEachSample = function(data, sort_order) {
  data = transform(data, method=factor(method, levels=LEVEL_C))

  ggplot(data, aes(x=gc_bin, y=coverage, group=Sample, color=Sample)) +
    facet_grid(method~.) +
    geom_line() +
    ggtitle('Average Coverage versus GC bias') +
    scale_y_continuous('Average Coverage (per sample)', label=format_comma) +
    xlab('GC Bias') +
    MY_THEME
}


# Function to plot boxplots of coverage distribution over samples per target interval
plotCovDistPerInterval = function(data) {
  unique_genes = unique(data$Gene)
  
  # Iterate over gene sets
  for (i in seq(1, length(unique_genes), 2)) {
    end = i + 2
    genes_subset = unique_genes[i : end]
    data_subset = data[data$Gene %in% genes_subset, ]
    plot_data = ggplot(data_subset, aes(x=probe, y=coverage)) +
      facet_grid(~gene, scales = 'free', space = 'free') +
      geom_boxplot(fill = hue_pal()(2)[2]) +
      theme(text = element_text(size=8), axis.text.x=element_blank(), axis.ticks.x=element_blank(), plot.margin = unit(c(.1, .1, .1, 1), 'in')) +
      ggtitle('Coverage for each Target Interval') +
      scale_y_continuous('Coverage', label=format_comma) +
      xlab('Target Interval')
    print(plot_data)
  }
}


#' Distribution of coverage across targets (total and unique)
#' Function to plot histogram of coverage per target interval distribution
#' Coverage values are scaled by the mean of the distribution
plotCovDistPerIntervalLine = function(data) {
  # n = length(unique(data$Sample))
  # cols = factor(gg_color_hue(n))
  
  data = data %>%
    group_by(Sample) %>%
    mutate(coverage_scaled = coverage / median(coverage))
  
  ggplot(data) +
    geom_line(aes(x=coverage_scaled, colour=Sample), stat='density') +
    ggtitle('Distribution of Coverages per Target Interval') +
    scale_y_continuous('Frequency', label=format_comma) +
    scale_x_continuous('Coverage', limits=c(0, 3)) +
    # scale_color_manual(values = cols) +
    MY_THEME
  
  # Use stat='bin' when testing on small data
  # ggplot(data) +
  #   geom_line(aes(x=coverage, colour=Sample), stat='bin', binwidth=0.5) +
  #   ggtitle('Distribution of Coverages per Target Interval') +
  #   scale_y_continuous('Frequency', label=format_comma) +
  #   MY_THEME
}


#' Plot the distribution of insert sizes (a.k.a. fragment lengths),
#' as well as most frequent insert sizes
#' @param insertSizes data.frame of insertSizes, ?
#' @param insertSizes data.frame of insertSizePeaks, ?
plotInsertSizeDistribution = function(insertSizes, insertSizePeaks) {
  totalFreq = insertSizes %>%
    group_by(Sample) %>%
    mutate(total_frequency_sum = sum(total_frequency)) %>%
    select(Sample, total_frequency_sum)

  peakSizes = insertSizePeaks %>%
    inner_join(totalFreq, by='Sample') %>%
    distinct() %>%
    mutate(total_frequency_fraction = peak_total / total_frequency_sum)

  insertSizes = insertSizes %>%
    group_by(Sample) %>%
    mutate(total_frequency_fraction = total_frequency / sum(total_frequency)) %>%
    ungroup()

  ggplot(insertSizes, aes(x=fragment_size, y=total_frequency_fraction, colour=Sample)) +
    # geom_smooth(size=.5, n=2000, span=.1, se=FALSE, method='loess', level=0.95) +
    # Use geom_line instead of geom_smooth for testing (not enough points)
    geom_line() +

#    geom_text_repel(
#      data = peakSizes,
#      size = 2,
#      segment.color = 'transparent',
#      force = 1,
#      direction = 'y',
#      show.legend = FALSE,
#      aes(x = Inf, y = Inf,
#      label = paste('peak_total_size: ', peak_total_size,  ', n = ', peak_total, sep = ''))) +

    scale_y_continuous(limits = c(0, max(insertSizes$total_frequency_fraction))) +
    ggtitle('Insert Size Distribution') +
    xlab('Insert Size') +
    ylab('Frequency') +
    MY_THEME
}


#' Print the title file to our PDF
#' @param title_df
printTitle = function(title_df) {
  mytheme <- gridExtra::ttheme_default(
    core = list(fg_params=list(cex = 0.4)),
    colhead = list(fg_params=list(cex = 0.5)),
    rowhead = list(fg_params=list(cex = 0.5)))
  
  # Remove some columns
  title_df = title_df[, !(names(title_df) %in% DROP_COLS)]
  
  # Split into two sections
  halfway = floor(ncol(title_df) / 2)
  title_df_two_subset = c(1, halfway : ncol(title_df))
  title_df_one = title_df[1 : halfway]
  title_df_two = title_df[, title_df_two_subset]
  tbl1 <- tableGrob(title_df_one, rows=NULL, theme=mytheme)
  tbl2 <- tableGrob(title_df_two, rows=NULL, theme=mytheme)
  
  title = textGrob(label = 'MSK-ACCESS QC Report')
  date = format(Sys.time(), '%a %b %d %Y %H:%M:%S')
  date = textGrob(label = date)
  # line = linesGrob(
            # x=unit(c(0, 1), 'npc'),
            # y=unit(c(0, 0), 'npc'),
            # default.units='npc',
            # arrow=NULL,
            # name=NULL,
            # gp=gpar(),
            # vp=NULL)
  line = linesGrob(
    unit(c(0.05, 0.95), 'npc'),
    unit(1, 'npc'),
    gp=gpar(col='lightgrey', lwd=4))
  
  # Todo: this is not a clean solution
  lay <- rbind(c(1,1,1,1,1),
               c(2,2,2,2,2),
               c(3,3,3,3,3),
               c(4,4,4,4,4),
               c(4,4,4,4,4),
               c(4,4,4,4,4),
               c(4,4,4,4,4),
               c(4,4,4,4,4),
               c(4,4,4,4,4),
               c(5,5,5,5,5),
               c(5,5,5,5,5),
               c(5,5,5,5,5),
               c(5,5,5,5,5),
               c(5,5,5,5,5),
               c(5,5,5,5,5))
  gs = list(title, date, line, tbl1, tbl2)
  grid.arrange(grobs=gs, layout_matrix=lay)
}


# Todo - demultiplexing stats (# reads per sample; # unexpected reads)
# Input would be folder of fastqs --> output would be histogram of # reads per fastq (cat asdf.fastq | head / 4...)
# problems may occur if 'undertermined' reads are in the folder as well...
# might already have the undertemined Bam though ... should check


#' Util function to merge various computed tables with original experiment title file
#' @param data data.frame to be used
#' @param title_df The title file as a data.frame
mergeInTitleFileData = function(data, title_df) {
  merged = merge(data, title_df, by.x='Sample', by.y='Sample')
  merged
}


#' Read in the sort_order file, which looks like:
#' sample_id
#' sample_id
#' sample_id
#' ...
#' @param groups_file Path to groups file
#' @deprecated?
parse_sort_order = function(groups_file) {
  sort_order = read.table(groups_file, sep='\t', fill=FALSE, strip.white=TRUE)
  sort_order = unlist(sort_order)
  return(sort_order)
}


# Extract actual sample names from full filenames
#' Ex: sample_names = c('test_patient_T', 'test_patient_N')
#' test_patient_T_001_aln_srt_MD_IR_FX_BR --> test_patient_T
cleanup_sample_names = function(data, sample_names) {
  find.string <- paste(unlist(sample_names), collapse = "|")
  find.string <- paste0('.*(', find.string, ').*', collapse='', sep='')
  data = data %>% mutate(Sample = gsub(find.string, '\\1', Sample))
  data
}


# Main function that will provide all of the desired plots
main = function(args) {
  # Read arguments specifying where the required tables are
  # as well as where the plots should be put
  # todo - should return an object or named list, instead of this indexed list 
  args = readInputs(args)
  inDirTables = args[1]
  inDirWaltz = args[2]
  outDir = args[3]
  title_file = args[4]

  title_df = read.table(title_file, sep='\t', header=TRUE)
  
  # Define the output PDF file
  date = format(Sys.time(), '%a-%b-%d-%Y_%H-%M-%S')
  final_filename = paste('qc_results', gsub('[:|/]', '-', date), 'pdf', sep='.')
  final_dest = paste(outDir, final_filename, sep="/")
  pdf(file = final_dest, onefile = TRUE)
  
  # Put title file on first page of PDF
  printTitle(title_df)

  # Title file sample colunn is used as sort order
  sort_order = unlist(title_df$Sample)

readCountsDataTotal = read.table(paste(inDirTables, 'read-counts-total.txt', sep='/'), sep='\t', head=TRUE)
dupRateData = read.table(paste(inDirTables, 'duplication-rates.txt', sep='/'), sep='\t', head=TRUE)
covPerInterval = read.table(paste(inDirTables, 'coverage-per-interval.txt', sep='/'), sep='\t', head=TRUE)
insertSizePeaks = read.table(paste(inDirTables, 'insert-size-peaks.txt', sep='/'), sep='\t', head=TRUE)
insertSizes = read.table(paste(inDirWaltz, 'fragment-sizes.txt', sep='/'), sep='\t', head=TRUE)
meanCovData = read.table(paste(inDirTables, 'coverage-agg.txt', sep='/'), sep='\t', head=TRUE)
gcAllSamples = read.table(paste(inDirTables, 'GC-bias-with-coverage-averages-over-all-samples.txt', sep='/'), sep='\t', head=TRUE)
gcEachSample = read.table(paste(inDirTables, 'GC-bias-with-coverage-averages-over-each-sample.txt', sep='/'), sep='\t', head=TRUE)

printhead = function(x) {
  print(head(x))
}

# Perform some processing on some of our tables
dfList <- list(readCountsDataTotal, dupRateData, covPerInterval, insertSizePeaks, insertSizes, meanCovData, gcEachSample)
dfList = lapply(dfList, cleanup_sample_names, sort_order)
dfList = lapply(dfList, sort_df, 'Sample', sort_order)
lapply(dfList, printhead)

dfList = lapply(dfList, mergeInTitleFileData, title_df)

readCountsDataTotal = dfList[[1]]
dupRateData = dfList[[2]]
covPerInterval = dfList[[3]]
insertSizePeaks = dfList[[4]]
insertSizes = dfList[[5]]
meanCovData = dfList[[6]]
gcEachSample = dfList[[7]]

# Choose the plots that we want to run
print(plotAlignGenome(readCountsDataTotal))
# print(plotCovDistPerInterval(covPerInterval))
print(plotOnTarget(readCountsDataTotal))
print(plotInsertSizeDistribution(insertSizes, insertSizePeaks))
print(plotCovDistPerIntervalLine(covPerInterval))
print(plotDupFrac(dupRateData))
print(plotMeanCov(meanCovData))
# print(plotGCwithCovAllSamples(gcAllSamples))
print(plotGCwithCovEachSample(gcEachSample, sort_order))

dev.off()
}


# Parse arguments
argv = commandArgs(trailingOnly=TRUE)
# Run main()
main(argv)
# Show warnings after running
warnings()
