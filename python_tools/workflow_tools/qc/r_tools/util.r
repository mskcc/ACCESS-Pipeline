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
suppressMessages(library(dplyr))


#' Util function to sort data by arbitrary list
#' @param df The data.frame to be sorted 
#' @param sort_column String - column to sort on
#' @param sort_list optional Vector of strings ordered in desired sort order for @df
sort_df = function(df, sort_column, sort_list) {
  if (!missing(sort_list)) {
    sort_list = unique(unlist(sort_list))
    sort_list = as.factor(sort_list)
    df[[sort_column]] <- factor(df[[sort_column]], levels=sort_list)
  } else {
    df[[sort_column]] <- factor(df[[sort_column]])
  }
  df = df[order(df[[sort_column]]),]
  return(df)
}


#' Function to read inputs from argv
#' @return object with parsed arguments
read_inputs = function() {
  spec = matrix(c(
    'tables_output_dir', 'i', 1, 'character',
    'title_file_path', 't', 1, 'character',
    'inputs_yaml_path', 'y', 1, 'character',
    'family_types_A_path', 'f', 1, 'character',
    'family_types_B_path', 'g', 1, 'character',
    'family_sizes_path', 'h', 1, 'character'
  ), byrow=TRUE, ncol=4);
  
  opts = getopt(spec);
  return(opts)
}


#' Util function to merge various computed tables with original experiment title file
#' @param data data.frame to be used
#' @param title_df The title file as a data.frame
merge_in_title_file_data = function(data, title_df) {
  merged = merge(
    data,
    title_df, 
    by=paste(SAMPLE_ID_COLUMN))
  
  return(merged)
}


#' Extract actual sample names from full filenames
#' 
#' @param data data.frame of sample manifest with proper CMO_SAMPLE_ID column
#' @param sample_names String[] with proper Sample IDs to be found
#' 
#' Ex: sample_names = c('test_sample_T', 'test_sample_N')
#' test_sample_T_001_aln_srt_MD_IR_FX_BR -> test_sample_T
cleanup_sample_names = function(data, sample_names) {
  # Need to reverse sort to get longer matches first - not necessary if '^' is used to indicate start of sample names
  sample_names = sample_names[order(nchar(sample_names), sample_names, decreasing = TRUE)]
  find.string = paste(paste0("^", unlist(sample_names)), collapse = '|')
  find.string = paste0('.*(', find.string, ').*', collapse='', sep='')
  data[, SAMPLE_ID_COLUMN] = gsub(find.string, '\\1', data[, SAMPLE_ID_COLUMN])
  return(data)
}
