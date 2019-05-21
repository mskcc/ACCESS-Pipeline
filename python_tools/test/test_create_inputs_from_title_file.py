import unittest
import pandas as pd

from constants import *
from python_tools.pipeline_kickoff import create_inputs_from_title_file


def load_bad_title_file():
    title_file = pd.read_csv('test_data/bad_title_file.txt', sep='\t')
    return title_file

def load_good_title_file_similar_sample_names():
    title_file = pd.read_csv('test_data/good_title_file_similar_sample_names.txt', sep='\t')
    return title_file

def load_good_title_file_with_difficult_sample_ids():
    title_file = pd.read_csv('test_data/good_title_file_difficult_sample_ids.txt', sep='\t')
    return title_file

def load_good_title_file():
    title_file = pd.read_csv('test_data/good_title_file.txt', sep='\t')
    return title_file


class CIFTTests(unittest.TestCase):

    def setUp(self):
        self.bad_title_file = load_bad_title_file()
        self.good_title_file = load_good_title_file()
        self.good_title_file_with_difficult_sample_ids = load_good_title_file_similar_sample_names()

        self._fastq_objects = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1/test_patient_1_test_investigator_sample_1_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1a/test_patient_1_test_investigator_sample_1a_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R1_001.fastq.gz'}
        ]

        # Use absolute paths
        self._fastq_objects = [
            {'class': 'File', 'path': os.path.abspath(p['path'])} for p in self._fastq_objects
        ]

        self._fastq2_objects = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1/test_patient_1_test_investigator_sample_1_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1a/test_patient_1_test_investigator_sample_1a_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R2_001.fastq.gz'}
        ]

        self._patient_ids = ['test_patient_1', 'test_patient_1', 'test_patient_2', 'test_patient_2', 'test_patient_2', 'test_patient_3']

        self._sample_sheets = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1a/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/SampleSheet.csv'}
        ]

        # Use absolute paths
        self._sample_sheets = [
            {'class': 'File', 'path': os.path.abspath(p['path'])} for p in self._sample_sheets
        ]


    def test_get_fastq_positions(self):

        fastq1, fastq2, sample_sheet = create_inputs_from_title_file.sort_fastqs(
            self._fastq_objects,
            self._fastq2_objects,
            self._sample_sheets,
            self.bad_title_file
        )

        expected = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1a/test_patient_1_test_investigator_sample_1a_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1/test_patient_1_test_investigator_sample_1_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R1_001.fastq.gz'},
        ]

        self.assertListEqual(fastq1, [{'class': 'File', 'path': os.path.abspath(f['path'])} for f in expected])


    def test_two_sample_ids_found_in_fastq(self):

        fastq_objects = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1a/test_patient_1_test_investigator_sample_1a_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1/test_patient_1_test_investigator_sample_1_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R1_001.fastq.gz'}
        ]

        fastq2_objects = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1a/test_patient_1_test_investigator_sample_1a_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1/test_patient_1_test_investigator_sample_1_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R2_001.fastq.gz'}
        ]

        sample_sheets = [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1a/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_1/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_3_N/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/SampleSheet.csv'}
        ]

        title_file = load_good_title_file_similar_sample_names()

        fastq1, fastq2, sample_sheet = create_inputs_from_title_file.sort_fastqs(
            fastq_objects,
            fastq2_objects,
            sample_sheets,
            title_file
        )

        self.assertListEqual(fastq1, [
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1/test_patient_1_test_investigator_sample_1_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_1_test_investigator_sample_1a/test_patient_1_test_investigator_sample_1a_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_4_T/test_patient_2_test_investigator_sample_4_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_3_N/test_patient_2_test_investigator_sample_3_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_2_test_investigator_sample_5_N/test_patient_2_test_investigator_sample_5_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../../test/test_data/umi-T_N-PanCancer/test_patient_3_test_investigator_sample_6_T/test_patient_3_test_investigator_sample_6_T_R1_001.fastq.gz'},
        ])


    def test_validate_title_file(self):
        """

        :return:
        """
        with self.assertRaises(Exception):
            create_inputs_from_title_file.perform_validation(self.bad_title_file)

        # Fix missing lane number
        self.bad_title_file.loc[self.bad_title_file.index[0], MANIFEST__LANE_COLUMN] = 1
        with self.assertRaises(Exception):
            create_inputs_from_title_file.perform_validation(self.bad_title_file)

        # Fix duplicate barcodes
        self.bad_title_file.loc[self.bad_title_file.index[-1], MANIFEST__BARCODE_ID_COLUMN] = 'bc411-bc411'
        with self.assertRaises(Exception):
            create_inputs_from_title_file.perform_validation(self.bad_title_file, 'test_project_title_file.txt', 'test_project')

        # Fix misspelled sample class
        self.bad_title_file[MANIFEST__SAMPLE_CLASS_COLUMN] = self.bad_title_file[MANIFEST__SAMPLE_CLASS_COLUMN].str.replace('Tumore', 'Tumor')
        with self.assertRaises(Exception) as context:
            create_inputs_from_title_file.perform_validation(self.bad_title_file)

        # Fix misspelled sample type
        self.bad_title_file[MANIFEST__SAMPLE_TYPE_COLUMN] = self.bad_title_file[MANIFEST__SAMPLE_TYPE_COLUMN].str.replace('Plasmaa', 'Plasma')

        # Now it should pass
        create_inputs_from_title_file.perform_validation(self.bad_title_file, 'test_project_title_file.txt', 'test_project')


    def test_barcodes_check(self):
        """
        Standalone test for barcodes validation

        :return:
        """
        with self.assertRaises(AssertionError):
            create_inputs_from_title_file.perform_barcode_index_checks_i7(
                self.good_title_file_with_difficult_sample_ids, self._sample_sheets)

        with self.assertRaises(AssertionError):
            create_inputs_from_title_file.perform_barcode_index_checks_i5(
                self.good_title_file_with_difficult_sample_ids, self._sample_sheets)

