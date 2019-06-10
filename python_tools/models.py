"""
Common models and data structures used in ACCESS_pipeline python_tools

Todo: Use this class wherever title_files are used
Todo: Consider creating an additional Sample class, and renaming this to SampleCollection
"""


import pandas as pd

from python_tools.constants import *


class TitleFile():
    """
    A wrapper around a pands.DataFrame object to allow consistent access of title file information
    """

    def __init__(self, title_file_path):
        """
        Instantiate a TitleFile object from a tab-delimited file with correct title file columns

        :param title_file_path:
        """
        self.__title_file__ = pd.read_csv(title_file_path, sep='\t')

    def get_cmo_sample_ids(self):
        """
        Return CMO_SAMPLE_ID column from title file as list

        :return:
        """
        return self.__title_file__[MANIFEST__CMO_SAMPLE_ID_COLUMN].tolist()

    def get_investigator_sample_ids(self):
        """
        Return INVESTIGATOR_SAMPLE_ID column from title file as list

        :return:
        """
        return self.__title_file__[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN].tolist()

    def get_patient_ids(self):
        """
        Return MANIFEST__CMO_PATIENT_ID_COLUMN column from title file as list

        Note: patient ID needs to be a string, in case it is currently an integer

        :return:
        """
        return [str(p) for p in self.__title_file__[MANIFEST__CMO_PATIENT_ID_COLUMN].tolist()]

    def get_sexes(self):
        """
        Return MANIFEST__SEX column from title file as list

        :return:
        """
        return self.__title_file__[MANIFEST__SEX_COLUMN].tolist()

    def get_lanes(self):
        """
        Return MANIFEST__LANE column from title file as list

        :return:
        """
        return self.__title_file__[MANIFEST__LANE_COLUMN].tolist()

    def get_barcode_ids(self):
        """
        Return MANIFEST__BARCODE_ID column from title file as list

        :return:
        """
        return self.__title_file__[MANIFEST__BARCODE_ID_COLUMN].tolist()
