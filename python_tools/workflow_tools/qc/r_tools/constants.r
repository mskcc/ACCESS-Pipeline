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
MSK_ORANGE = '#F98400' #'#D14124'
MSK_BLUE = '#0076A8'
MSK_LIGHT_BLUE = '#4492C6'
MSK_GREY = '#B3B3A1'

CONTINUOUS_COLOR_PALETTE = 'Rushmore1'

# Title file columns
# Consider using https://blog.rstudio.com/2018/03/26/reticulate-r-interface-to-python/
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

# Sample Classes
NORMAL = "Normal"
TUMOR = "Tumor"
POOLTUMOR = "PoolTumor"
POOLNORMAL = "PoolNormal"

# Easier name for sample ID column
SAMPLE_ID_COLUMN = TITLE_FILE__SAMPLE_ID_COLUMN

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
