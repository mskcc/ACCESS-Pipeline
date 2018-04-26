#! /usr/bin/env Rscript

#######################################################
# Innovation-QC Module
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# maintainer: Ian Johnson (johnsoni@mskcc.org)
#######################################################

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
  format(x, ..., big.mark = ",", scientific = FALSE, trim = TRUE)
}

# Flag to indicate usage of a title file 
# (default false)
USING_TITLE_FILE = FALSE

# Define our global plots theme
MY_THEME = theme(text = element_text(size=8),
  axis.text.x = element_text(angle = 45, hjust = 1, face="bold"),
  plot.margin = unit(c(.1, .1, .1, 1), "in"))

# Optional distinctive color palette
#' @param n Number of distinct colors to be returned
#' @return List of distinct colors (hue, luminance, contrast)?
gg_color_hue <- function(n) {
  hues = seq(15, 375, length = n + 1)
  lums = seq(0, 100, length = n + 1)
  hcl(h = hues, l = 65, c = 100)[1:n]
}

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

#' Util function to shorten sample names by removing a found search string
#' @param df The data.frame to be sorted
#' @param split Regex to be removed from entries in @columns
abbreviate_sample_names = function(df, split) {
  df = df %>% mutate(Sample = gsub(split, '', Sample))
  return(df)
}

#' Function to read inputs and obtain the previously created tables
#' @param args Arguments from argv
#' @return Parsed list of (
#'   tables_output_dir_location,
#'   standard_waltz_output_dir_location,
#'   output_dir_for_plots,
#'   title_file_path, (null if groups_file_path provided)
#'   groups_file_path (null if title_file_path provided)
#' )
readInputs = function(args) {
  spec = matrix(c(
    'standardWaltz', 'w', 1, "character",
    'tablesOutputDir', 'i', 1, "character",
    'plotsOutputDir', 'o', 1, "character",
    'titleFilePath', 't', 2, "character",
    'groupsFilePath', 'g', 2, "character"
  ), byrow=TRUE, ncol=4);
  
  opts = getopt(spec);
  
  if (!is.null(opts$titleFilePath) & !is.null(opts$groupsFilePath)) {
    stop("Cannot provide both Title File and Groups File")
  } else if (!is.null(opts$titleFilePath)) {
    # Set the flag to indicate that we are using a title file
    USING_TITLE_FILE <<- TRUE
  }
  
  if ( is.null(opts$standardWaltz ) ) { opts$standardWaltz = getwd() }
  if ( is.null(opts$tablesOutputDir ) ) { opts$tablesOutputDir = getwd() }
  if ( is.null(opts$plotsOutputDir ) ) { opts$plotsOutputDir = getwd() }
  
  if (USING_TITLE_FILE)
    return(c(opts$tablesOutputDir, opts$standardWaltz, opts$plotsOutputDir, opts$titleFilePath))
  else
    return(c(opts$tablesOutputDir, opts$standardWaltz, opts$plotsOutputDir, opts$groupsFilePath))
}

# Function to plot duplication fraction (Standard Bams only)
#' @param data data.frame with the usual columns
plotDupFrac = function(data) {
  # Plot may be used across collapsing methods, or with T/N coloring for just total values
  # data = transform(data, Method=factor(Method,levels=c("Total", "Picard", "marianas_unfiltered", "marianas_simplex_duplex", 'marianas_duplex')))
  data = data %>% filter(Method == "Picard")
  
  if("Class" %in% colnames(data)) {
    fill_var = 'Class'
  } else {
    fill_var = 'Method'
  }
  
  ggplot(data, aes(x = Sample, y = as.numeric(DuplicationRate))) +
    geom_bar(stat="identity", aes_string(fill = fill_var), position = "dodge") +
    ggtitle("Duplication Rate per Sample") +
    scale_y_continuous("Duplication Rate", label=format_comma) +
    MY_THEME
}

# Function to plot number of reads that aligned to the reference genome
#' @param data data.frame with the usual columns
plotAlignGenome = function(data) {
  if("Class" %in% colnames(data)) {
    fill_var = "Class"
  } else {
    fill_var = "Sample"
  }
  
  ggplot(data, aes(x = Sample, y = AlignFrac)) +
    geom_bar(position = "dodge", stat="identity", aes_string(fill = fill_var)) +
    ggtitle("Fraction of Total Reads that Align to the Human Genome") +
    scale_y_continuous("Fraction of Reads", label=format_comma) + 
    MY_THEME
}

#' Plot average coverage for each sample,
#' for each collapsing method
#' @param data data.frame with the usual columns
plotMeanCov = function(data) {
  # Specify sort order of Method
  data = transform(data, Method=factor(Method, levels=c("Total", "Picard", "marianas_unfiltered", 'marianas_simplex_duplex', "marianas_duplex")))
  
  if("Class" %in% colnames(data)) {
    fill_var = 'Class'
  } else {
    fill_var = 'Method'
  }
  
  ggplot(data, aes(x = Sample, y = AverageCoverage)) +
    facet_grid(Method~ ., , scales = "free") +
    geom_bar(position = "dodge", stat="identity", aes_string(fill = fill_var)) +
    ggtitle("Average Coverage per Sample for Each Collapsing Method") +
    scale_y_continuous("Average Coverage", label=format_comma) +
    MY_THEME
}

#' Plot on target rate 
#' (usually a metric for standard bams)
#' @param data data.frame with the usual columns
plotOnTarget = function(data) {
  ggplot(melt(data[c("Sample", "TotalOnTargetFraction", "TotalOffTargetFraction")], id = "Sample"), aes(x = Sample, y = value)) +
    geom_bar(position = position_stack(reverse = TRUE), stat="identity", aes(fill = variable)) +
    ggtitle("Fraction of Total On/Off Target Reads") +
    scale_y_continuous("Fraction of Reads", label=format_comma) + 
    MY_THEME
}

#' Plot Coverage vs %GC content, averaged over all samples 
#' (for each collapsing method)
#' @param data data.frame with the usual columns
plotGCwithCovAllSamples = function(data) {
  data = transform(data, Method=factor(Method,levels=c("Total", "Picard", "marianas_unfiltered", "marianas_simplex_duplex", 'marianas_duplex')))
  
  ggplot(data, aes(x = GCbin, y = Coverage, color = Method, group = Method)) +
    geom_line() +
    ggtitle("Average Coverage versus GC bias for each Collapsing Method") +
    scale_y_continuous("Average Coverage (all samples)", label=format_comma) +
    xlab("GC bias") + 
    MY_THEME
}

#' Plot Coverage vs %GC content, separately for each sample 
#' (for each collapsing method)
#' @param data data.frame with the usual columns
plotGCwithCovEachSample = function(data, sort_order) {
  data = transform(data, Method=factor(Method, levels=c("Total", "Picard", "marianas_unfiltered", "marianas_simplex_duplex", 'marianas_duplex')))
  # Todo - Should standardize
  data = data %>% mutate(Sample = gsub('FulcrumCollapsed_', '', Sample))
  data = sort_df(data, 'Sample', sort_order)

  ggplot(data, aes(x = GCbin, y = Coverage, group = Sample, color = Sample)) +
    facet_grid(Method~.) +
    geom_line() +
    ggtitle("Average Coverage versus GC bias for each Collapsing Method") +
    scale_y_continuous("Average Coverage (per sample)", label=format_comma) +
    xlab("GC bias") +
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
    plot_data = ggplot(data_subset, aes(x = Probe, y = Coverage)) +
      facet_grid(~Gene, scales = "free", space = "free") +
      geom_boxplot(fill = hue_pal()(2)[2]) +
      theme(text = element_text(size=8), axis.text.x=element_blank(), axis.ticks.x=element_blank(), plot.margin = unit(c(.1, .1, .1, 1), "in")) +
      ggtitle("Coverage for each Target Interval") +
      scale_y_continuous("Coverage", label=format_comma) +
      xlab("Target Interval")
    print(plot_data)
  }
}

#' Distribution of coverage across targets (total and unique)
#' Function to plot histogram of coverage per target interval distribution
#' Coverage values are scaled by the mean of the distribution
plotCovDistPerIntervalLine = function(data) {
  n = length(unique(data$Sample))
  cols = factor(gg_color_hue(n))
  
  data = data %>%
    group_by(Sample) %>%
    mutate(coverage_scaled = Coverage / median(Coverage))
  
  ggplot(data) +
    geom_line(aes(x=coverage_scaled, colour=Sample), stat="density") +
    ggtitle("Distribution of Coverages per Target Interval") +
    scale_y_continuous("Frequency", label=format_comma) +
    scale_x_continuous("Coverage", limits = c(0, 3)) +
    # scale_color_manual(values = cols) +
    MY_THEME
}

#' Plot the distribution of insert sizes (a.k.a. fragment lengths),
#' as well as most frequent insert sizes
#' @param insertSizes data.frame of insertSizes, ?
#' @param insertSizes data.frame of insertSizePeaks, ?
plotInsertSizeDistribution = function(insertSizes, insertSizePeaks) {
  totalFreq = insertSizes %>%
    group_by(Sample) %>%
    mutate(TotalFrequencySum = sum(TotalFrequency)) %>%
    select(Sample, TotalFrequencySum)

  peakSizes = insertSizePeaks %>%
    inner_join(totalFreq, by="Sample") %>%
    distinct() %>%
    mutate(TotalFrequencyFraction = PeakTotal / TotalFrequencySum)

  insertSizes = insertSizes %>%
    group_by(Sample) %>%
    mutate(TotalFrequencyFraction = TotalFrequency / sum(TotalFrequency)) %>%
    ungroup()

  ggplot(insertSizes, aes(x=FragmentSize, y=TotalFrequencyFraction, colour=Sample)) +
    stat_smooth(size=.5, n=200, span=0.2, se=FALSE, method="loess", level=.01) +

    geom_text_repel(
      data = peakSizes,
      size = 2,
      segment.color = 'transparent',
      force = 1,
      direction = "y",
      show.legend = FALSE,
      aes(x = Inf, y = Inf,
      label = paste("PeakTotalSize: ", PeakTotalSize, ", n = ", PeakTotal, sep = ''))) +

    scale_y_continuous(limits = c(0, max(insertSizes$TotalFrequencyFraction))) +
    ggtitle("Insert Size Distribution for all Samples") +
    xlab("Insert Size") +
    MY_THEME
}

#' Print the title file to our PDF
#' @param title_df
printTitle = function(title_df) {
  mytheme <- gridExtra::ttheme_default(
    core = list(fg_params=list(cex = 0.4)),
    colhead = list(fg_params=list(cex = 0.5)),
    rowhead = list(fg_params=list(cex = 0.5)))
  
  # Split into two sections
  halfway = floor(ncol(title_df) / 2)
  title_df_two_subset = c(1, halfway : ncol(title_df))
  title_df_one = title_df[1 : halfway]
  title_df_two = title_df[, title_df_two_subset]
  tbl1 <- tableGrob(title_df_one, rows=NULL, theme=mytheme)
  tbl2 <- tableGrob(title_df_two, rows=NULL, theme=mytheme)
  
  grid.draw(textGrob(label = "Innovation QC Report"))
  
  # Use viewports to arrange the tables
  sample_vp_1 <- viewport(x = 0.5, y = 0.75, 
                          width = 0.9, height = 0.4,
                          just = c("center", "center"))
  sample_vp_2 <- viewport(x = 0.5, y = 0.25, 
                          width = 0.9, height = 0.4,
                          just = c("center", "center"))
  
  pushViewport(sample_vp_1)
  grid.draw(tbl1)
  popViewport()
  pushViewport(sample_vp_2)
  grid.draw(tbl2)
  popViewport()
} 

# Todo - demultiplexing stats (# reads per sample; # unexpected reads)
# Input would be folder of fastqs --> output would be histogram of # reads per fastq (cat asdf.fastq | head / 4...)
# problems may occur if "undertermined" reads are in the folder as well...
# might already have the undertemined Bam though ... should check

#' Util function to merge various computed tables with original experiment title file
#' @param data data.frame to be used
#' @param title_df The title file as a data.frame
mergeInTitleFileData = function(data, title_df) {
  merged = merge(data, title_df, by.x='Sample', by.y='Sample')
  
  # Again, covering all bases
  if (nrow(merged) == 0) {
    title_df = title_df %>% mutate(Sample = gsub('-IGO.*', '', Sample))
    merged = merge(data, title_df, by.x='Sample', by.y='Sample')
  }  
  
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
  sort_order = read.table(groups_file, sep="\t", fill=FALSE, strip.white=TRUE)
  sort_order = unlist(sort_order)
  return(sort_order)
}

#' Run this on a data.frame to provide consistent sample names to our sample ids
#' @param data data.frame with 'Sample' column
#' @param format either 'DASHES' or 'UNDERSCORES'
#' @deprecated?
convert_sample_names = function(data, format) {
  if (format == 'DASHES') {
    data = data %>% mutate(Sample = gsub('_', '-', Sample))
  } else if (format == 'UNDERSCORES') {
    data = data %>% mutate(Sample = gsub('-', '_', Sample))
  } else {
    stop("Incorrect sample id format provided")
  }
  data
}


cleanup_sample_names = function(data, sample_names) {
  data = convert_sample_names(data, 'DASHES')
  
  data = data %>% mutate(Sample = gsub('_md', '', Sample))
  data = data %>% mutate(Sample = gsub('-md', '', Sample))
  data = data %>% mutate(Sample = gsub('.bam', '', Sample))
  data = data %>% mutate(Sample = gsub('Sample_', '', Sample))
  data = data %>% mutate(Sample = gsub('Sample-', '', Sample))
  data = data %>% mutate(Sample = gsub('Sample', '', Sample))
  data = data %>% mutate(Sample = gsub('_IGO.*', '', Sample))
  data = data %>% mutate(Sample = gsub('-IGO.*', '', Sample))
  
  # Ex: sample_names = c('test_patient_T', 'test_patient_N')
  # test_patient_T_001_aln_srt_MD_IR_FX_BR --> test_patient_T
  find.string <- paste(unlist(sample_names), collapse = "|")
  find.string <- paste0('.*(', find.string, ').*', collapse='', sep='')
  data = data %>% mutate(Sample = gsub(find.string, '\\1', Sample))
  
  # Ex: ZS-msi-4506-pl-T01_IGO_05500_EF_41_S41_standard...
  data = data %>% mutate(Sample = gsub('_standard.*', '', Sample))
  
  # Ex: ZS-msi-4506-pl-T01_IGO_05500_EF_41_S41
  #                                       ^^^^
  data = data %>% mutate(Sample = gsub('_.\\d\\d$', '', Sample))
  data
}

#' Util function to try a lot of sample id formats, to cover all our bases
#' todo - eliminating this method is part of ongoing sample id formatting issues
#' @param sort_order list of sample ids, with no particular formatting
#' @return vector of variations of sort_order entries
generate_sort_order_combinations = function(sort_order) {
  times = rep(9, length(sort_order))
  
  sort_order = rep(sort_order, times)
  sort_order = as.vector(sort_order)
  
  for (i in seq_along(sort_order)) {
    if (i %% 9 == 1) {
      # Replace all dashes with underscores
      sort_order[[i]] <- gsub('-', '_', sort_order[[i]])
    } else if (i %% 9 == 2) {
      # Replace all underscores with dashes
      sort_order[[i]] = gsub('_', '-', sort_order[[i]])
    } else if (i %% 9 == 3) {
      # Remove trailing .bam
      sort_order[[i]] = gsub('.bam', '', sort_order[[i]])
    } else if (i %% 9 == 4) {
      # Add trailing .bam
      sort_order[[i]] = paste(sort_order[[i]], '.bam', sep='')
    } else if (i %% 9 == 5) {
      # Remove Sample_
      sort_order[[i]] = gsub('Sample_', '', sort_order[[i]])
    } else if (i %% 9 == 6) {
      # Remove trailing .bam and replace underscores with dashes
      tmp = gsub('.bam', '', sort_order[[i]])
      sort_order[[i]] = gsub('_', '-', tmp)
    } else if (i %% 9 == 7) {
      # Remove everything after "-IGO"
      sort_order[[i]] = gsub('-IGO.*', '', sort_order[[i]])
    } else if (i %% 9 == 8) {
      # Remove everything after "_IGO"
      sort_order[[i]] = gsub('_IGO.*', '', sort_order[[i]])
    }
  }
  return(sort_order)
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
  # todo - rename "title" or "groups"
  title_file = args[4]
  
  # Define the output PDF file
  date = format(Sys.time(), '%a-%b-%d-%Y_%H-%M-%S')
  final_filename = paste("qc_results", gsub("[:|/]", "-", date), "pdf", sep=".")
  final_dest = paste(outDir, final_filename, sep="/")
  pdf(file = final_dest, onefile = TRUE)
      
  # Use either the title_file or the groups_file to sort and label the samples
  if (USING_TITLE_FILE) {
    title_df = read.table(title_file, sep='\t', header=TRUE)
    
    # Check if the title_file had the correct delimiter
    if (length(colnames(title_df)) == 1) {
      title_df = read.table(title_file, sep=',', header=TRUE)
    }
    
    # Put title file on first page of PDF
    printTitle(title_df)
    
    # Todo - get columns names right
    if ("SampleID" %in% colnames(title_df)) {
      title_df = rename(title_df, Sample = SampleID)
    } else if ("Sample_ID" %in% colnames(title_df)) {
      title_df = rename(title_df, Sample = Sample_ID)
    }
    sort_order = unlist(title_df$Sample)
    
    # We prefer dashes
    title_df = convert_sample_names(title_df, 'DASHES')
  } else {
    sort_order = parse_sort_order(title_file)
  }
  # Try matching different sample id formats
  sort_order = generate_sort_order_combinations(sort_order)
  sort_order = generate_sort_order_combinations(sort_order)
  
  availTabs = list.files(path = inDirTables)
  if ("read-counts-total.txt" %in% availTabs) {
    readCountsDataTotal = read.table(paste(inDirTables, "read-counts-total.txt", sep = "/"), sep = "\t", head = TRUE)
    dupRateData = read.table(paste(inDirTables, "duplication-rates.txt", sep = "/"), sep = "\t", head = TRUE)
    covPerInterval = read.table(paste(inDirTables, "coverage-per-interval.txt", sep = "/"), sep = "\t", head = TRUE)
    insertSizePeaks = read.table(paste(inDirTables, "insert-size-peaks.txt", sep = "/"), sep = "\t", head = TRUE)
    insertSizes = read.table(paste(inDirWaltz, "fragment-sizes.txt", sep="/"), sep="\t", head=TRUE)
    
    printhead = function(x) {
      print(head(x))
    }
    
    # Perform some processing on some of our tables
    dfList <- list(readCountsDataTotal, dupRateData, covPerInterval, insertSizePeaks, insertSizes)
    dfList = lapply(dfList, convert_sample_names, 'DASHES')
    dfList = lapply(dfList, cleanup_sample_names, sort_order)
    dfList = lapply(dfList, sort_df, 'Sample', sort_order)
    lapply(dfList, printhead)
    
    # Optionally merge in the title file data for plotting purposes
    if (USING_TITLE_FILE) {
      dfList = lapply(dfList, mergeInTitleFileData, title_df)
    }
    readCountsDataTotal = dfList[[1]]
    dupRateData = dfList[[2]]
    covPerInterval = dfList[[3]]
    insertSizePeaks = dfList[[4]]
    insertSizes = dfList[[5]]

    # Choose the plots that we want to run
    print(plotDupFrac(dupRateData))
    print(plotAlignGenome(readCountsDataTotal))
    # print(plotCovDistPerInterval(covPerInterval))
    print(plotOnTarget(readCountsDataTotal))
    print(plotInsertSizeDistribution(insertSizes, insertSizePeaks))
    print(plotCovDistPerIntervalLine(covPerInterval))
  }

  meanCovData = read.table(paste(inDirTables, "coverage-agg.txt", sep="/"), sep="\t", head = TRUE)
  gcAllSamples = read.table(paste(inDirTables, "GC-bias-with-coverage-averages-over-all-samples.txt", sep="/"), sep="\t", head=TRUE)
  gcEachSample = read.table(paste(inDirTables, "GC-bias-with-coverage-averages-over-each-sample.txt", sep="/"), sep="\t", head=TRUE)
  
  # Perform some processing on some of our (other) tables
  dfList <- list(meanCovData, gcEachSample)
  dfList = lapply(dfList, convert_sample_names, 'DASHES')
  dfList = lapply(dfList, cleanup_sample_names)
  dfList = lapply(dfList, sort_df, 'Sample', sort_order)
  
  # Optionally merge in the title file data for plotting purposes
  if (USING_TITLE_FILE) {
    dfList = lapply(dfList, mergeInTitleFileData, title_df)
  }
  
  meanCovData = dfList[[1]]
  gcEachSample = dfList[[2]]

  print(plotMeanCov(meanCovData))
  print(plotGCwithCovAllSamples(gcAllSamples))
  print(plotGCwithCovEachSample(gcEachSample, sort_order))
  dev.off()
}


# Parse arguments and run main()
argv = commandArgs(trailingOnly=TRUE)
main(argv)
