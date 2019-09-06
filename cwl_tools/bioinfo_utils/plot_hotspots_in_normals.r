#! /usr/bin/env Rscript

library(grid)
library(dplyr)
library(scales)
library(ggplot2)
library(gridExtra)

INPUT_TABLE_FILENAME = 'hotspots-in-normals.txt'
OUTPUT_PLOT_FILENAME = 'hotspots_in_normals.pdf'

THEME = theme(
  text = element_text(size=24),
  axis.text.x = element_text(angle=45, hjust=1, face='bold'),
  axis.text.y = element_text(face='bold'),
  plot.margin = unit(c(.1, .1, .1, 1), 'in')
)

counts = read.table(
    INPUT_TABLE_FILENAME,
    sep = '\t',
    header = TRUE,
    colClasses = c(rep('character', 4), rep('numeric', 3))
)

if (nrow(counts) == 0) {
    pdf(file = OUTPUT_PLOT_FILENAME, height=15, width=20, onefile=TRUE)
    no_hotspots_msg = textGrob(label = 'No hotspots found', gp=gpar(fontsize=22, col='black'))
    grid.draw(no_hotspots_msg)
    dev.off()
    quit()
}

counts$Sample = reorder(counts$Sample, counts$SampleType=='Tumor')

g = ggplot(filter(counts, AltCount>0), aes(Sample, Mutation)) +
    theme_bw() +
    geom_point(aes(color=SampleType, size=AF, shape=15)) +
    scale_shape_identity() +
    geom_text(aes(label=paste(sep='', AF, ' (', AltCount, '/', Total, ')')), vjust=0, nudge_y = -0.60, size=6) +
    ggtitle('Hotspot mutations in normals (normals: unfiltered, tumors: duplex, > 3 fragments)') +
    THEME

ggsave(g, file=OUTPUT_PLOT_FILENAME, width=20, height=20)
    