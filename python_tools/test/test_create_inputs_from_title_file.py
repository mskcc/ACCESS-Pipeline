import unittest
import pandas as pd

from constants import *
from python_tools.pipeline_kickoff import create_inputs_from_title_file


def load_bad_title_file():
    title_file = pd.read_csv('test_data/bad_title_file.txt', sep='\t')
    return title_file


def load_good_title_file():
    title_file = pd.read_csv('test_data/good_title_file.txt', sep='\t')
    return title_file


class Tests(unittest.TestCase):

    def setUp(self):
        self.bad_title_file = load_bad_title_file()
        self.good_title_file = load_good_title_file()

        self._fastq_objects = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_2_T/test_patient_1_test_investigator_sample_2_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1_N/test_patient_1_test_investigator_sample_1_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R1_001.fastq.gz'}
        ]

        self._fastq2_objects = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_2_T/test_patient_1_test_investigator_sample_2_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1_N/test_patient_1_test_investigator_sample_1_N_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R2_001.fastq.gz'}
        ]

        self._patient_ids = ['test_patient_1', 'test_patient_1', 'test_patient_2', 'test_patient_2', 'test_patient_2', 'test_patient_3']

        self._sample_sheets = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_2_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1_N/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/SampleSheet.csv'}
        ]


    def test_get_fastq_positions(self):

        fastq1, fastq2, sample_sheet = create_inputs_from_title_file.sort_fastqs(
            self._fastq_objects,
            self._fastq2_objects,
            self._sample_sheets,
            self.bad_title_file
        )

        assert fastq1 == [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_2_T/test_patient_1_test_investigator_sample_2_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1_N/test_patient_1_test_investigator_sample_1_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R1_001.fastq.gz'},
        ]

    def test_validate_title_file(self):
        """

        :return:
        """
        with self.assertRaises(Exception):
            create_inputs_from_title_file.perform_validation(self.bad_title_file)

        # Fix duplicate barcodes
        self.bad_title_file.loc[self.bad_title_file.index[-1], MANIFEST__BARCODE_ID_COLUMN] = 'bc411-bc411'

        with self.assertRaises(Exception):
            create_inputs_from_title_file.perform_validation(self.bad_title_file)

        # Fix misspelled sample class
        self.bad_title_file[MANIFEST__SAMPLE_CLASS_COLUMN] = self.bad_title_file[MANIFEST__SAMPLE_CLASS_COLUMN].str.replace('Tumore', 'Tumor')

        with self.assertRaises(Exception) as context:
            create_inputs_from_title_file.perform_validation(self.bad_title_file)

        # Fix misspelled sample type
        self.bad_title_file[MANIFEST__SAMPLE_TYPE_COLUMN] = self.bad_title_file[MANIFEST__SAMPLE_TYPE_COLUMN].str.replace('Plasmaa', 'Plasma')

        # Now it should pass
        create_inputs_from_title_file.perform_validation(self.bad_title_file)


    def test_barcodes_check(self):
        """

        :return:
        """
        create_inputs_from_title_file.perform_barcode_index_checks(self.good_title_file, self._sample_sheets)
