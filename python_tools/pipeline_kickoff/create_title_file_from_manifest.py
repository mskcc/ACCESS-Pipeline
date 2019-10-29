import xlrd
import logging
import argparse
import pandas as pd

from python_tools.legacy_constants import *


# Pipeline Kickoff Step #1
#
# This module is used to create a title file with the information formatted for a pipeline run
# It is derived from the manually-generated sample manifest (usually an .xlsx file)
#
# Usage example:
#
# create_title_file_from_manifest \
#   -i ./manifest.xlsx \
#   -o ./title_file.txt


def convert_to_title_file(manifest):
    """
    Perform operations to turn our manifest into a well-formatted title file for the pipeline

    :param manifest:
    :return:
    """
    sample_info = manifest['SampleInfo']
    sample_renames = manifest['SampleRenames']

    # Select the columns we want from the manifest & rename them
    try:
        title_file = sample_info.loc[:, manifest_columns]
    except KeyError as e:
        logging.error('Error, missing manifest columns')
        logging.error('Existing manifest columns:')
        logging.error(sample_info.columns)
        raise e

    # Use SampleRenames tab to convert CMO_SAMPLE_ID to proper CMO ID
    sample_rename_map = dict(zip(sample_renames['OldName'], sample_renames['NewName']))
    sample_convert_func = lambda sample: sample_rename_map[sample]
    title_file.loc[:, MANIFEST__CMO_SAMPLE_ID_COLUMN] = title_file[MANIFEST__CMO_SAMPLE_ID_COLUMN].apply(sample_convert_func)

    # Select the columns we want from the manifest & rename them
    title_file = manifest[columns_map_manifest.keys()]
    title_file.columns = columns_map_manifest.values()

    # Remove empty rows
    title_file = title_file.dropna(axis=0, how='all')

    # Trim whitespace
    trim_func = lambda series: series.str.strip() if series.dtype == 'object' else series
    title_file = title_file.apply(trim_func)

    # Fix overly-high precision values from Excel
    title_file = title_file.round(3)

    return title_file


def create_title_file(manifest_file_path, output_filename):
    """
    Read manifest and convert to title file

    :param manifest_file_path:
    :param output_filename:
    :return:
    """

    # Read as either csv or Excel file
    try:
        manifest = pd.read_excel(manifest_file_path, sheetname=['SampleInfo', 'SampleRenames'], sep='\t')
    except (xlrd.biffh.XLRDError, pd.io.common.CParserError) as e:
        print(str(e))
        manifest = pd.read_csv(manifest_file_path, sep='\t')

    title_file = convert_to_title_file(manifest)

    # Optionally split by lanes
    if len(title_file[MANIFEST__PROJECT_ID_COLUMN].unique()) > 1:
        path, filename = os.path.split(output_filename)

        for project_id in title_file[MANIFEST__PROJECT_ID_COLUMN].unique():
            title_file_sub = title_file[title_file[MANIFEST__PROJECT_ID_COLUMN] == project_id]
            output_filename = project_id + '_' + filename
            output_file_path = os.path.join(path, output_filename)
            title_file_sub.to_csv(output_file_path, sep='\t', index=False)
    else:
        title_file.to_csv(output_filename, sep='\t', index=False)

########
# Main #
########

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--manifest_file_path", help="Sample Manifest File (e.g. test_manifest.xlsx)", required=True)
    parser.add_argument("-o", "--output_filename", help="Desired output title location and name", required=True)

    args = parser.parse_args()
    create_title_file(args.manifest_file_path, args.output_filename)


if __name__ == "__main__":
    main()
