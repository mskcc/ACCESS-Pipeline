'''
@Description : This tool tests remove_variants
@Created :  03/23/2017
@Updated : 03/23/2017
@author : Ronak H Shah, @ionox0
'''

import os
import nose
import pandas as pd

from pandas.util.testing import assert_frame_equal

from cwl_tools.remove_variants.remove_variants import (
    make_coordinate_for_complex_variants,
    consolidate_overlapping_complex_variants,
    remove_intergenic_variants,
)


def read_maf():
    """
    Read the test input maf to be filtered. Create additional data frame of Complex variants

    :param args:
    :return:
    """
    this_dir, this_filename = os.path.split(__file__)
    inputFileMaf = os.path.join(this_dir, 'test_data', 'sample_input.maf')

    df = pd.read_table(inputFileMaf, comment='#', low_memory=False)
    complex_variant_df = df.loc[df['TYPE'] == 'Complex']
    return complex_variant_df, df


def test_remove_variants():
    """

    :return:
    """
    cvDF, mafDF = read_maf()
    posToCheck = make_coordinate_for_complex_variants(cvDF)
    clean_maf = consolidate_overlapping_complex_variants(posToCheck, mafDF)
    clean_maf = remove_intergenic_variants(clean_maf)

    this_dir, this_filename = os.path.split(__file__)
    expected_maf = os.path.join(this_dir, 'test_data', 'sample_output.maf')
    expected = pd.read_table(expected_maf, comment='#', low_memory=False)

    # Need to finagle able to compare DataFrames
    # Todo: Just create a new expected file
    clean_maf.dropna(how='any', inplace=True)
    expected.dropna(how='any', inplace=True)
    clean_maf.iloc[:,117] = clean_maf.iloc[:,117].astype(int)
    expected.iloc[:,117] = expected.iloc[:,117].astype(int)
    clean_maf = clean_maf.sort_index().sort_index(axis=1).round(5).astype(str).reset_index(drop=True)
    expected = expected.sort_index().sort_index(axis=1).round(5).astype(str).reset_index(drop=True)

    # Let's limit ourselves to just three test cases:
    # 1. Variant_Classificaton == 'IGR' event is filtered
    # 2. Complex Vardict event overlapping with MuTect SNP is consolidated (MuTect variant is lost) --> Or should we remove this functionality?
    # 3. ~10 variants with neither of these^ are not filtered
    # == 12 variants

    assert_frame_equal(clean_maf, expected)


if __name__ == '__main__':
    nose.main()
