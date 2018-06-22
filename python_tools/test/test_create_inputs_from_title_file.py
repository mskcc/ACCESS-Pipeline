import unittest
import pandas as pd
from python_tools.pipeline_kickoff import create_inputs_from_title_file

from constants import *


def load_title_file():
    title_file = pd.read_csv('test_data/XX_title_file.txt', sep='\t')
    return title_file


class Tests(unittest.TestCase):

    def setUp(self):

        self._title_file = load_title_file()

        self._fastq_objects = [
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_1_test_sample_2_T/test_patient_1_test_sample_2_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_1_test_sample_1_N/test_patient_1_test_sample_1_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_4_T/test_patient_2_test_sample_4_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_3_N/test_patient_2_test_sample_3_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_3_test_sample_6_T/test_patient_3_test_sample_6_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_5_N/test_patient_2_test_sample_5_N_R1_001.fastq.gz'}
        ]

        self._fastq2_objects = [
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_1_test_sample_2_T/test_patient_1_test_sample_2_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_1_test_sample_1_N/test_patient_1_test_sample_1_N_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_4_T/test_patient_2_test_sample_4_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_3_N/test_patient_2_test_sample_3_N_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_3_test_sample_6_T/test_patient_3_test_sample_6_T_R2_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_5_N/test_patient_2_test_sample_5_N_R2_001.fastq.gz'}
        ]

        self._patient_ids = ['test_patient_1', 'test_patient_1', 'test_patient_2', 'test_patient_2', 'test_patient_2', 'test_patient_3']

        self._sample_sheets = [
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_1_test_sample_2_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_1_test_sample_1_N/SampleSheet.csv'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_4_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_3_N/SampleSheet.csv'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_3_test_sample_6_T/SampleSheet.csv'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_5_N/SampleSheet.csv'}
        ]


    def test_get_fastq_positions(self):

        fastq1, fastq2, sample_sheet = create_inputs_from_title_file.sort_fastqs(
            self._fastq_objects,
            self._fastq2_objects,
            self._sample_sheets,
            self._title_file
        )

        print fastq1

        assert fastq1 ==  [
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_1_test_sample_2_T/test_patient_1_test_sample_2_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_1_test_sample_1_N/test_patient_1_test_sample_1_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_4_T/test_patient_2_test_sample_4_T_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_3_N/test_patient_2_test_sample_3_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_2_test_sample_5_N/test_patient_2_test_sample_5_N_R1_001.fastq.gz'},
            {'class': 'File', 'path': '../Innovation-Pipeline/test/test_data/umi-T_N-PanCancer/test_patient_3_test_sample_6_T/test_patient_3_test_sample_6_T_R1_001.fastq.gz'},
        ]
