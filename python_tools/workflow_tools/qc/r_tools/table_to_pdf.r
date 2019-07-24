#! /usr/bin/env Rscript

library(grid)
library(dplyr)
library(scales)
library(ggplot2)
library(gridExtra)

# Read in a file, and print it to a PDF as a table
# sys.argv[1] - string - Filename of table. Must be tab-separated with header
# sys.argv[2] - string - Filename to give to output plot

INPUT_TABLE_FILENAME = sys.argv[1]
OUTPUT_PLOT_FILENAME = sys.argv[2]


THEME = theme(
    text = element_text(size=24),
    axis.text.x = element_text(angle=45, hjust=1, face='bold'),
    axis.text.y = element_text(face='bold'),
    plot.margin = unit(c(.1, .1, .1, 1), 'in')
)

table = read.table(
    INPUT_TABLE_FILENAME,
    sep = '\t',
    header = TRUE,
)

# Handle the case where the table is empty
if (nrow(counts) == 0) {
    empty_table_msg = paste('Empty table for ', INPUT_TABLE_FILENAME)
    pdf(file = OUTPUT_PLOT_FILENAME, height=15, width=20, onefile=TRUE)
    empty_grob = textGrob(label = empty_table_msg, gp=gpar(fontsize=22, col='black'))
    grid.draw(empty_grob)
    dev.off()
    quit()
}

# Convert to grob
# Define the output PDF file
pdf(file = OUTPUT_PLOT_FILENAME, height=15, width=20, onefile=TRUE)
table_grob = tableGrob(table, rows=NULL, theme=THEME)
grid.draw(table_grob)
dev.off()
