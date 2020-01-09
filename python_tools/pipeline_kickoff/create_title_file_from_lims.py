import json
import base64
import argparse
import requests

import pandas as pd

from python_tools.constants import TITLE_FILE__COLUMN_ORDER


# Endpoint constants
LIMS_API_URL = 'https://igolims.mskcc.org:8443'

LIMS_REQUEST_ID_ENDPOINT = '/LimsRest/api/getRequestSamples'
LIMS_REQUEST_PARAM = 'request'

LIMS_MANIFEST_ENDPOINT = '/LimsRest/api/getSampleManifest'
LIMS_SAMPLE_ID_PARAM = 'igoSampleId'


def parse_args():
    """
    Create and parse args with argparse

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--credentials_file', required=True, help='Path to credentials')
    parser.add_argument('-r', '--igo_request_id', required=True, help='IGO request ID to create manifest for')
    parser.add_argument('-o', '--output_file_name', required=True, help='Name to give to output title file')
    args = parser.parse_args()
    return args


def get_sample_info_for_request_id(credentials_file, igo_request_id):
    """
    Format request for sample info for given IGO request ID

    :param igo_request_id:
    :return:
    """
    username, password = open(credentials_file).read().split()
    encoded_credentials = base64.b64encode(username + ':' + password)
    headers = {'Authorization': 'Basic ' + encoded_credentials}
    print(headers)

    IGO_REQUEST_REQUEST = LIMS_API_URL + \
                          LIMS_REQUEST_ID_ENDPOINT + '?' + \
                          LIMS_REQUEST_PARAM + '=' + igo_request_id

    sample_info = requests.get(IGO_REQUEST_REQUEST, headers=headers, verify=False).json()
    sample_ids = [sample['igoSampleId'] for sample in sample_info['samples']]
    # Todo: endpoint is limited to 10 samples per query...
    sample_ids = sample_ids[0:5]

    SAMPLE_INFO_REQUEST = LIMS_API_URL + \
                          LIMS_MANIFEST_ENDPOINT + '?' + \
                          LIMS_SAMPLE_ID_PARAM + '=' + \
                          ','.join(sample_ids)

    print(SAMPLE_INFO_REQUEST)
    manifest_info = requests.get(SAMPLE_INFO_REQUEST, headers=headers, verify=False).json()

    return manifest_info


def create_title_file(args):
    """
    Create title file from IGO request ID

    :return:
    """
    sample_info = get_sample_info_for_request_id(args.credentials_file, args.igo_request_id)

    # Todo: how to deal with multiple libraries / runs?
    # Todo: why is libraries array empty sometimes?
    title_file = [
        [
            sample['libraries'][0]['barcodeId'],
            sample['libraries'][0]['captureName'],
            sample['sampleName'],
            sample['investigatorSampleId'],
            sample['cmoPatientId'],
            sample['tumorOrNormal'],
            sample['cmoSampleClass'], # todo: correct?
            sample['libraries'][0]['libraryVolume'], # todo: no library input ng info available?
            sample['libraries'][0]['libraryVolume'], # todo: no library yield available?
            sample['libraries'][0]['captureInputNg'],
            sample['baitSet'],
            sample['sex'],
            sample['libraries'][0]['barcodeIndex'],
            sample['libraries'][0]['barcodeIndex'], # todo: get barcode index 2
            sample['libraries'][0]['runs'][0]['flowCellLanes'][0], # todo, fix pipeline to allow multiple lanes?
        ]

        for sample in sample_info
    ]

    df = pd.DataFrame(title_file, columns=TITLE_FILE__COLUMN_ORDER)
    df.to_csv(args.output_file_name, sep='\t', index=False)


def main():
    args = parse_args()
    create_title_file(args)

if __name__ == '__main__':
    main()