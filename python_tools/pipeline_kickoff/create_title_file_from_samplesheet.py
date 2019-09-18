#!/usr/bin/env python
import xlrd
import argparse
import pandas as pd

from python_tools.constants import *

# Suppress pandas copy warning
pd.options.mode.chained_assignment = None

##################################
# Pipeline Kickoff Step #1
#
# This module is used to create a title file with the information needed for a pipeline run
# It is derived from the manually-curated sample samplesheet
#
# Usage example:
#
# create_title_file_from_samplesheet \
#   -i ./SampleSheet.csv \
#   -o ./title_file.txt
#
# Note: The following requirements will be imposed on the input samplesheet file:
#
# 1. The fields that are found in the sample samplesheet should matched with the examples in test/test_data
# 2. The sample ID's in the samplesheet must be matched somewhere in the fastq file names fom the -d data folder
# 3. The sample ID's in the samplesheet must be matched somewhere in the path to the SampleSheet.csv files
# 4. The SAMPLE_CLASS column of the samplesheet must consist of the values either "Tumor" or "Normal"
# 5. Each "Tumor" sample must have at least one associated "Normal" sample
# 6. Each sample folder in the -d data folder must have these three files:
#
# '_R1_001.fastq.gz'
# '_R2_001.fastq.gz'
# 'SampleSheet.csv'


def create_title_file(samplesheet_file_path, output_filename):
    """
    Main function to read sample sheet, perform checks 
    """
    ### Read samplesheet as either csv or Excel file ###
    try:
        samplesheet = pd.read_csv(samplesheet_file_path, sep=",", header=0)
    except (xlrd.biffh.XLRDError, pd.io.common.CParserError):
        samplesheet = pd.read_excel(samplesheet_file_path, sep=",")

    # Remove rows where all elements are missing
    samplesheet = samplesheet.dropna(axis=0, how="all")
    samplesheet = samplesheet.replace("\n", "", regex=True)

    ### resolve columns values ###
    # Check for duplicate columns
    if not samplesheet.equals(samplesheet.loc[:, ~samplesheet.columns.duplicated()]):
        raise Exception("Duplicated column headers in samplesheet.")

    # Check for required columns
    if not set(SAMPLE_SHEET_REQUIRED_COLUMNS) <= set(samplesheet.columns.tolist()):
        missing_columns = set(SAMPLE_SHEET_REQUIRED_COLUMNS) ^ set(
            samplesheet.columns.tolist()
        )
        raise Exception(
            "SampleSheet is missing the following required columns: {}.".format(
                ",".join(missing_columns)
            )
        )

    # Check for optional columns
    if set(SAMPLE_SHEET_REQUIRED_COLUMNS + SAMPLE_SHEET_OPTIONAL_COLUMNS) < set(
        samplesheet.columns.tolist()
    ):
        unrecognized_columns = set(
            SAMPLE_SHEET_REQUIRED_COLUMNS + SAMPLE_SHEET_OPTIONAL_COLUMNS
        ) ^ set(samplesheet.columns.tolist())
        print("WARNING: SampleSheet has additional unrecognized columns: {}").format(
            ",".join(unrecognized_columns)
        )
    elif set(SAMPLE_SHEET_REQUIRED_COLUMNS + SAMPLE_SHEET_OPTIONAL_COLUMNS) > set(
        samplesheet.columns.tolist()
    ):
        missing_columns = set(
            SAMPLE_SHEET_REQUIRED_COLUMNS + SAMPLE_SHEET_OPTIONAL_COLUMNS
        ) ^ set(samplesheet.columns.tolist())
        print(
            "WARNING: SampleSheet is missing the following optional columns: {}"
        ).format(",".join(missing_columns))

    ### resolve row values ###
    # Check if required column values are populated for all rows
    if not samplesheet.equals(samplesheet.dropna(subset=SAMPLE_SHEET_REQUIRED_COLUMNS)):
        raise Exception("Missing values in require columns.")

    # Select the explicitly defined columns we want from the samplesheet & rename them
    try:
        title_file = samplesheet[columns_map_samplesheet.keys()]
    except KeyError:
        raise Exception("Cannot map sample sheet columns to title file.")

    title_file.columns = columns_map_samplesheet.values()

    # populate title file barcode column
    try:
        title_file[TITLE_FILE__BARCODE_ID_COLUMN] = [
            barcode_x if barcode_x == barcode_y else barcode_x + "_" + barcode_y
            for barcode_x, barcode_y in zip(
                samplesheet[SAMPLE_SHEET__BARCODE_ID1_COLUMN],
                samplesheet[SAMPLE_SHEET__BARCODE_ID2_COLUMN],
            )
        ]
    except (KeyError, ValueError):
        raise Exception("Error while populating barcode values in the title file.")

    # check for projectID and bait version
    def projectid_format(id):
        """
        helper function to check project ID and extract bait version.
        """
        if PROJECT_NAME.match(id):
            try:
                return BAIT_SEARCH.findall(id).pop().replace(ASSAY_NAME, "")
            except IndexError:
                raise Exception(
                    "Bait version cannot be identified from project/run ID."
                )
        else:
            raise Exception("Project ID is not in the required format.")

    # Get bait version from project ID and perform check
    title_file[TITLE_FILE__BAIT_VERSION_COLUMN] = title_file[
        TITLE_FILE__POOL_COLUMN
    ].apply(projectid_format)
    if len(set(title_file[TITLE_FILE__BAIT_VERSION_COLUMN])) > 1:
        raise Exception("Samplesheet contains samples with mutliple bait version.")
    if (
        not set(title_file[TITLE_FILE__BAIT_VERSION_COLUMN]).pop()
        == EXPECTED_BAIT_VERSION
    ):
        raise Exception("Samplesheet bait version does not match the expected value.")

    # sample description/class check
    if not set(title_file[TITLE_FILE__SAMPLE_CLASS_COLUMN]) <= set(
        ALLOWED_SAMPLE_DESCRIPTION
    ):
        raise Exception(
            "Unexpected sample description. Only the following sample descritpions are allowed: {}.".format(
                ",".join(ALLOWED_SAMPLE_DESCRIPTION)
            )
        )

    # split metadata column
    try:
        title_file[
            [
                TITLE_FILE__PATIENT_NAME_COLUMN,
                TITLE_FILE__ACCESSION_COLUMN,
                TITLE_FILE__SEX_COLUMN,
                TITLE_FILE__SEQUENCER_COLUMN,
            ]
        ] = samplesheet[SAMPLE_SHEET__METADATA_COLUMN].str.split(
            METADATA_COLUMN_DELIMETER, expand=True
        )[
            METADATA_REQUIRED_COLUMNS
        ]
    except (ValueError, KeyError):
        raise Exception(
            "Operator column values are improperly defined. There should be at least 5 '|' delimited fields in this order: OperatorName|PatientName|Accession|Sex|Sequencer"
        )

    # SEX column makes sense?
    title_file.loc[
        title_file[TITLE_FILE__SEX_COLUMN].isin(CONTROL_SAMPLE_SEX),
        TITLE_FILE__SEX_COLUMN,
    ] = FEMALE
    if not set(title_file[TITLE_FILE__SEX_COLUMN]) <= set(ALLOWED_SEX):
        raise Exception(
            "Unrecognized SEX type. Should be one of: {}.".format(
                ",".join(ALLOWED_SEX + CONTROL_SAMPLE_SEX)
            )
        )

    # Check sequencer columns
    if not set(title_file[TITLE_FILE__SEQUENCER_COLUMN]) <= set(ALLOWED_SEQUENCERS):
        unrecognized_values = set(title_file[TITLE_FILE__SEQUENCER_COLUMN]) ^ set(
            ALLOWED_SEQUENCERS
        )
        raise Exception(
            "Unrecognized sequencer names: {}".format(",".join(unrecognized_values))
        )
    if len(set(title_file[TITLE_FILE__SEQUENCER_COLUMN])) > 1:
        raise Exception(
            "Only one unique sequencer name is allowerd per title file. There are: {}".format(
                ",".join(set(title_file[TITLE_FILE__SEQUENCER_COLUMN]))
            )
        )

    # check sample id and sample name format
    def name_check(sampleid):
        """
        helper function to validate sample IDs and names.
        """
        if any([s1 in sampleid for s1 in DISALLOWED_SAMPLE_ID_CHARACTERS]):
            raise Exception(
                "Disallowed characters in {}. Ensure that none of the following characters exist: {}".format(
                    sampleid, DISALLOWED_SAMPLE_ID_CHARACTERS
                )
            )

    title_file[TITLE_FILE__SAMPLE_ID_COLUMN].apply(name_check)
    title_file[TITLE_FILE__PATIENT_ID_COLUMN].apply(name_check)

    # infer sample type from sample id
    try:
        title_file[TITLE_FILE__SAMPLE_TYPE_COLUMN] = title_file[
            TITLE_FILE__SAMPLE_ID_COLUMN
        ].str.split(SAMPLE_ID_ALLOWED_DELIMETER, 1, expand=True)[SELECT_SPLIT_COLUMN]
    except KeyError:
        raise Exception(
            "Error when interpreting sample type from sample_id. Ensure the sample-id are in the 00000000-X format."
        )

    # inferred sample type check
    def sample_type_check(sample):
        if not ALLOWED_SAMPLE_TYPE.match(sample):
            raise Exception(
                "Unknown sample type {}. Sample type should start with one of: {}".format(
                    sample, ",".join(ALLOWED_SAMPLE_TYPE_LIST)
                )
            )

    title_file[TITLE_FILE__SAMPLE_TYPE_COLUMN].apply(sample_type_check)
    # if not set(title_file[TITLE_FILE__SAMPLE_TYPE_COLUMN]) <= set(ALLOWED_SAMPLE_TYPE):
    #     raise Exception(
    #         "Unexpected sample type. Only the following sample types are allowed: {}.".format(
    #             ",".join(ALLOWED_SAMPLE_TYPE)
    #         )
    #     )

    # Assign sample type
    title_file[TITLE_FILE__SAMPLE_TYPE_COLUMN] = [
        PLASMA if PLASMA_SAMPLE_TYPE.match(x) else BUFFY
        for x in title_file[TITLE_FILE__SAMPLE_TYPE_COLUMN]
    ]

    # constant columns
    title_file[TITLE_FILE__COLLAB_ID_COLUMN] = COLLAB_ID

    # Samplesheet does not include this information at the moment
    # TODO: DMS can work out a way to fill this info if required.
    title_file[TITLE_FILE__POOL_INPUT_COLUMN] = ""

    # Trim whitespace
    title_file = title_file.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Optionally split by lanes
    if len(title_file[TITLE_FILE__LANE_COLUMN].unique()) > 1:
        duplicate_samples = []
        for lane in title_file[TITLE_FILE__LANE_COLUMN].unique():
            duplicate_samples.extend(
                title_file[title_file[TITLE_FILE__LANE_COLUMN] == lane][
                    TITLE_FILE__SAMPLE_ID_COLUMN
                ].tolist()
            )
        duplicate_samples = list(
            filter(lambda x: duplicate_samples.count(x) > 1, duplicate_samples)
        )
        columns_to_consider = title_file.columns.tolist()
        columns_to_consider.remove(TITLE_FILE__LANE_COLUMN)
        title_file = title_file.drop_duplicates(subset=columns_to_consider)
        title_file[TITLE_FILE__LANE_COLUMN].loc[
            title_file[TITLE_FILE__SAMPLE_ID_COLUMN].isin(duplicate_samples)
        ] = MERGED_LANE_VALUE
        title_file = title_file[TITLE_FILE__COLUMN_ORDER]
        title_file.to_csv(output_filename, sep="\t", index=False)
    else:
        title_file = title_file[TITLE_FILE__COLUMN_ORDER]
        title_file.to_csv(output_filename, sep="\t", index=False)


########
# Main #
########


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--samplesheet_file_path",
        help="Sample Manifest File (e.g. test_samplesheet.xlsx)",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output_filename",
        help="Desired output title location and name",
        required=True,
    )

    args = parser.parse_args()
    create_title_file(args.samplesheet_file_path, args.output_filename)


if __name__ == "__main__":
    main()
