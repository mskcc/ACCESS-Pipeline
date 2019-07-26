#
# Generic plotting functions for ACCESS plots
#
import matplotlib
# For Luna:
matplotlib.use('Agg')
from matplotlib import pyplot as plt

# Constants to be used across all ACCESS plots
# Todo: fill in THEME dicts with seaborn / matplotlib kwargs
MATPLOTLIB_THEME = {}
SEABORN_THEME = {}
PLOT_HEIGHT = 8
PLOT_WIDTH = 7
FIGSIZE = (PLOT_HEIGHT, PLOT_WIDTH)
PLOT_MARGINS = (0.1, 0.1, 0.1, 0.1)
FONT_SIZE = 14
FONT_SIZE_LARGE = 16

# Locations for text in cells
TABLE_LOC = 'center'
TABLE_CELL_LOC = 'center'
TABLE_ROW_LOC = 'center'



def barplot():
    """
    Todo: Define function for ACCESS barplot

    :return:
    """
    pass


def lineplot():
    """
    Todo: Basic ACCESS lineplot with no faceting

    :return:
    """
    pass


def table(df, thing_being_plotted, title=None, suptitle=None, output_file_name='table.pdf'):
    """
    Given a pandas DataFrame, print a formatted table to a PDF

    Prints an empty table if `df` has no rows

    :param: df - pandas.DataFrame to be printed
    :param: thing_being_plotted - string A simple description of the data to be plotted
    :param: title - string Title for table
    """
    # sns.set(font_scale=.6)
    # Todo: need this^ here? Or works when only put at the top?

    plt.clf()
    fig, ax1 = plt.subplots(figsize=FIGSIZE)
    # Todo: Different from figsize?
    # fig.set_figheight(1)
    ax1.axis('off')
    ax1.axis('tight')

    if title:
        plt.title(title, fontsize=FONT_SIZE_LARGE)
    if suptitle:
        fig.suptitle(suptitle, fontsize=FONT_SIZE_LARGE)#, y=.5)

    if len(df):
        # Table has rows to print
        ax1.table(
            cellText=df.values,
            colLabels=df.columns,
            loc=TABLE_LOC,
            cellLoc=TABLE_CELL_LOC,
            rowLoc=TABLE_ROW_LOC
        )
    else:
        # Table is empty, make an empty row with same number of columns as df
        empty_values = [[('No ' + thing_being_plotted + ' present') * df.shape[1]]]
        ax1.table(
            cellText=empty_values,
            colLabels=df.columns,
            loc=TABLE_LOC,
            cellLoc=TABLE_CELL_LOC,
            rowLoc=TABLE_ROW_LOC
        )

    fig.tight_layout()
    plt.savefig(output_file_name, bbox_inches='tight')
