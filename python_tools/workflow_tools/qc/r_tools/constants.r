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


# Set terminal display width, error tracebacks
options(width=1000)
options(show.error.locations = TRUE)
options(error = quote({dump.frames(to.file=TRUE); q()}))
options(error=function()traceback(2))

# Util for putting commas in scale labels
format_comma <- function(x, ...) {
  format(x, ..., big.mark = ',', scientific = FALSE, trim = TRUE)
}

# Define our global plots theme
MAIN_PLOT_THEME = theme_light() + theme(
  text = element_text(size=10),
  axis.text.x = element_text(angle = 45, hjust = 1, face='bold'),
  plot.margin = unit(c(.1, .1, .1, 1), 'in')
)


TITLE_PAGE_THEME <- gridExtra::ttheme_default(
  base_size=18,
  core = list(
    fg_params=list(cex = .6),
    padding=unit(c(5, 3), "mm")
  ),
  colhead = list(fg_params=list(cex = 0.5)),
  rowhead = list(fg_params=list(cex = 0.5))
)

# Color variables
MSK_ORANGE = '#D67236' #'#F2300F' #'#D14124'
MSK_BLUE = '#5B1A18' #'#274150' #'#0076A8'
MSK_LIGHT_BLUE = '#FD6467' #'#9FA682' #'#4492C6'
MSK_GREY = '#F1BB7B' #'#E1BD6D' #'#B3B3A1'

CONTINUOUS_COLOR_PALETTE = 'Rushmore1'

# Title file columns
# Consider using https://blog.rstudio.com/2018/03/26/reticulate-r-interface-to-python/
#TITLE_FILE__BARCODE_ID_COLUMN = 'BARCODE_ID'
#TITLE_FILE__CAPTURE_NAME_COLUMN = 'CAPTURE_NAME'
#TITLE_FILE__CMO_SAMPLE_ID_COLUMN = 'CMO_SAMPLE_ID'
#TITLE_FILE__INVESTIGATOR_SAMPLE_ID_COLUMN = 'INVESTIGATOR_SAMPLE_ID'
#TITLE_FILE__CMO_PATIENT_ID_COLUMN = 'CMO_PATIENT_ID'
#TITLE_FILE__SAMPLE_CLASS_COLUMN = 'SAMPLE_CLASS'
#TITLE_FILE__SAMPLE_TYPE_COLUMN = 'SAMPLE_TYPE'
#TITLE_FILE__LIBRARY_INPUT_COLUMN = 'LIBRARY_INPUT[ng]'
#TITLE_FILE__LIBRARY_YIELD_COLUMN = 'LIBRARY_YIELD[ng]'
#TITLE_FILE__CAPTURE_INPUT_COLUMN = 'CAPTURE_INPUT[ng]'
#TITLE_FILE__CAPTURE_BAIT_SET_COLUMN = 'CAPTURE_BAIT_SET'
#TITLE_FILE__SEX_COLUMN = 'SEX'
#TITLE_FILE__LANE_NUMBER_COLUMN = 'LANE_NUMBER'
#TITLE_FILE__BARCODE_INDEX_1_COLUMN = 'BARCODE_INDEX_1'
#TITLE_FILE__BARCODE_INDEX_2_COLUMN = 'BARCODE_INDEX_2'
TITLE_FILE__BARCODE_ID_COLUMN               = 'Barcode'
TITLE_FILE__POOL_COLUMN                     = 'Pool'
TITLE_FILE__SAMPLE_ID_COLUMN                = 'Sample'
TITLE_FILE__COLLAB_ID_COLUMN                = 'Collab_ID'
TITLE_FILE__PATIENT_ID_COLUMN               = 'Patient_ID'
#TITLE_FILE__CLASS_COLUMN                    = 'Class'
TITLE_FILE__SAMPLE_CLASS_COLUMN             = 'Class'
TITLE_FILE__SAMPLE_TYPE_COLUMN              = 'Sample_type'
TITLE_FILE__INPUT_NG_COLUMN                 = 'Input_ng'
TITLE_FILE__LIBRARY_YIELD_COLUMN            = 'Library_yield'
TITLE_FILE__POOL_INPUT_COLUMN               = 'Pool_input'
TITLE_FILE__BAIT_VERSION_COLUMN             = 'Bait_version'
TITLE_FILE__SEX_COLUMN                      = 'Sex'
TITLE_FILE__BARCODE_INDEX_1_COLUMN          = 'Barcode_index_1'
TITLE_FILE__BARCODE_INDEX_2_COLUMN          = 'Barcode_index_2'
TITLE_FILE__LANE_COLUMN                     = 'Lane'


# Easier name for sample ID column
SAMPLE_ID_COLUMN = TITLE_FILE__SAMPLE_ID_COLUMN

# Some title file columns will not be printed
#DROP_COLS = c(
#  TITLE_FILE__CAPTURE_NAME_COLUMN,
#  TITLE_FILE__CAPTURE_INPUT_COLUMN,
#  TITLE_FILE__BARCODE_ID_COLUMN,
#  TITLE_FILE__PATIENT_ID_COLUMN,
#  TITLE_FILE__LIBRARY_YIELD_COLUMN,
#  TITLE_FILE__BARCODE_INDEX_1_COLUMN,
#  TITLE_FILE__BARCODE_INDEX_2_COLUMN
#)

DROP_COLS = c(
  TITLE_FILE__BAIT_VERSION_COLUMN,
  TITLE_FILE__INPUT_NG_COLUMN,
  TITLE_FILE__BARCODE_ID_COLUMN,
  TITLE_FILE__PATIENT_ID_COLUMN,
  TITLE_FILE__LIBRARY_YIELD_COLUMN,
  TITLE_FILE__BARCODE_INDEX_1_COLUMN,
  TITLE_FILE__BARCODE_INDEX_2_COLUMN
)

# Optional distinctive color palette
#' @param n Number of distinct colors to be returned
#' @return List of distinct colors (hue, luminance, contrast)?
gg_color_hue <- function(n) {
  hues = seq(15, 375, length = n + 1)
  lums = seq(0, 100, length = n + 1)
  hcl(h = hues, l = 65, c = 100)[1:n]
}
