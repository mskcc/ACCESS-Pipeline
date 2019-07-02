#!/usr/bin/env python

from __future__ import print_function
from collections import defaultdict, OrderedDict
from datetime import datetime
from glob import glob
import os, sys, argparse, requests, json

API_URL_PRODN = 'https://igo.mskcc.org:8443/velox_webservice/api/datarecord/'
API_URL_DEVEL = 'https://tango.mskcc.org:8443/velox_webservice/api/datarecord/'
SAPIO_GUID = 'fe74d8e1-c94b-4002-a04c-eb5c492704ba'

# General purpose wrapper around a GET call to the LIMS REST API
def get_call(api_url, endpoint, creds, params):
    headers = { 'Accept': 'application/json', 'guid': SAPIO_GUID }
    r = requests.get(api_url + endpoint, verify=False, headers=headers, auth=creds, params=params)
    if r.status_code is not 200:
        print(r.text)
        r.raise_for_status()
    return r.json()

# Return the Request record for a specific IGO request ID
def get_request(request_id, api_url, creds):
    params = { 'datatype': 'Request', 'field': 'RequestId', 'values': request_id }
    # Returns a list of records and IGO guarantees 1 record per request ID, but check anyway
    requests = get_call(api_url, '', creds, params)
    if len(requests) < 1:
        raise Exception('No matching record for IGO request ID: ' + request_id)
    elif len(requests) > 1:
        raise Exception('More than 1 matching record for IGO request ID: ' + request_id)
    return requests[0]

# Return the Project record that a specific IGO request belongs to
def get_project(request_record_id, api_url, creds):
    params = { 'datatype': 'Request', 'record_id': request_record_id, 'parent_datatype': 'Project' }
    # This returns a list of lists, of which we want the first record in the first list
    return get_call(api_url, 'parent', creds, params)[0][0]

# Return Sample records of type Library belonging to a specific IGO request ID
def get_libraries(request_id, api_url, creds):
    params = { 'datatype': 'Sample', 'field': 'RequestId', 'values': request_id }
    samples = get_call(api_url, '', creds, params)
    libraries = list(filter(lambda x : 'Library' in x['fields']['ExemplarSampleType'], samples))
    if len(libraries) < 1:
        raise Exception('No library records found under IGO request ID: ' + request_id)
    return libraries

# Return Sample records of type Pooled Library in which a specific sample ended up in
def get_pools(sample_record_id, api_url, creds):
    params = { 'datatype': 'Sample', 'record_id': sample_record_id, 'descendant_datatype': 'Sample' }
    # This returns a list of lists, of which we want the first list
    samples = get_call(api_url, 'descendant', creds, params)[0]
    pools = list(filter(lambda x : 'Pooled Library' in x['fields']['ExemplarSampleType'], samples))
    return pools

# Return sequencer run records in which a specific library was sequenced
def get_runs(sample_record_id, api_url, creds):
    params = { 'datatype': 'Sample', 'record_id': sample_record_id, 'ancestor_datatype': 'IlluminaSeqExperiment' }
    # This returns a list of lists, of which we want the first list
    return get_call(api_url, 'ancestor', creds, params)[0]

if __name__ == '__main__':
    # Fetch command-line arguments, set defaults, and print documentation when appropriate
    parser = argparse.ArgumentParser(description='Extract data from IGO LIMS to generate input files for Roslin')
    parser.add_argument('--request', type=str, required=True, help='an IGO request ID e.g. 04966_G')
    parser.add_argument('--out-dir', type=str, required=False, default='.', help='output folder where files will be generated')
    parser.add_argument('--legacy', action='store_true', help='generate additional files that use older BIC formats')
    parser.add_argument('--dev', action='store_true', help='use data from the development LIMS instead of from production')
    args = parser.parse_args()

    # Load credentials from a file next to this script, and disable security warnings
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'connect_lims.txt'), 'r') as fh:
        username = fh.readline().strip()
        password = fh.readline().strip()
    creds = requests.auth.HTTPBasicAuth(username, password)
    requests.packages.urllib3.disable_warnings()
    # Use the development or production API URL as requested by user
    api_url = API_URL_DEVEL if args.dev else API_URL_PRODN

    request_id = args.request
    request = get_request(request_id, api_url, creds)
    project = get_project(request['recordId'], api_url, creds)
    rdict = request['fields']
    pdict = project['fields']

    # Initialize a dictionary of data that will end up in the request file
    req_data = OrderedDict()
    req_data['ProjectID'] = 'Proj_' + request_id
    # ::TODO:: ProjectName will need some exception handling since we need it for automated merges
    req_data['ProjectName'] = rdict['CMOProjectID'] if rdict['CMOProjectID'] else pdict['CMOProjectID']
    req_data['ProjectTitle'] = pdict['CMOFinalProjectTitle']
    req_data['ProjectDesc'] = pdict['CMOProjectBrief']

    # Prefer PM-edited fields for contact info, before looking at IGO-edited fields
    req_data['PI_Name'] = rdict['PILastName'] + ', ' + rdict['PIFirstName'] if rdict['PILastName'] else rdict['LaboratoryHead']
    req_data['PI_E-mail'] = rdict['PIemail'] if rdict['PIemail'] else rdict['LabHeadEmail']
    req_data['PI'] = rdict['PIemail'].split('@')[0] if rdict['PIemail'] else rdict['LabHeadEmail'].split('@')[0]
    req_data['Investigator_Name'] = rdict['Investigator']
    req_data['Investigator_E-mail'] = rdict['Investigatoremail']
    req_data['Investigator'] = rdict['Investigatoremail'].split('@')[0] if '@' in rdict['Investigatoremail'] else ''
    req_data['Data_Analyst'] = rdict['DataAnalyst'] if rdict['DataAnalyst'] else ''
    req_data['Data_Analyst_E-mail'] = rdict['DataAnalystEmail'] if rdict['DataAnalystEmail'] else ''
    req_data['Project_Manager'] = rdict['ProjectManager']

    # Fetch data from the sample-level and deduplicate for the request file
    species = list()
    libraries = get_libraries(request_id, api_url, creds)
    for sample in libraries:
        if sample['fields']['Species'] not in species:
            species.append(sample['fields']['Species'])
    req_data['Species'] = ','.join(species)

    req_data['DateOfLastUpdate'] = datetime.fromtimestamp(int(rdict['RecentDeliveryDate'])/1000).strftime("%Y-%m-%d") if rdict['RecentDeliveryDate'] else ''
    req_data['NumberOfSamples'] = rdict['SampleNumber']
    req_data['Institution'] = 'cmo'

    # ::TODO:: Need to figure out the following, but some of these can be abandoned
    req_data['Project_Manager_Email'] = '##CANT ACCESS: NEED TO CREATE LOCAL MAP OF PM EMAIL?'
    req_data['Assay'] = '##BUILD FROM SAMPLES?'
    req_data['Run_Pipeline'] = '##BUILD FROM SAMPLES?'
    req_data['RunNumber'] = '##IDK'
    req_data['RunID'] = '##BUILD FROM SAMPLES'
    req_data['AmplificationTypes'] = '#To confirm- always NA or blank?'
    req_data['LibraryTypes'] = '##BUILD FROM SAMPLES?'
    req_data['Strand'] = '##BUILD FROM SAMPLES?'
    req_data['Pipelines'] = '##BUILD FROM SAMPLES?'
    req_data['ProjectFolder'] = '## Can be from /ifs/projects/CMO/, /ifs/projects/BIC/rnaseq/, /ifs/projects/BIC/other'
    req_file = os.path.join(args.out_dir, 'Proj_' + request_id + '_request.txt')
    with open(req_file, 'w') as req_fh:
        req_fh.write('\n'.join('{}: {}'.format(k,v) for k,v in req_data.items()) + '\n')

    # ::TODO:: legacy should only prevent creation of BIC sample_mapping.txt format, not our new fastq_manifest.txt format
    if not args.legacy:
        exit()

    # Maintain a list of flowcells for each library in the request, to help deduplicate
    flowcells = defaultdict(list)

    # For each library in the request, find pooled libraries it ended up in, and the flowcells all those libraries ended up in
    bic_mapping = list()
    for library in libraries:
        library_id = library['fields']['SampleId']
        pools = get_pools(library['recordId'], api_url, creds)
        for pool in pools:
            runs = get_runs(pool['recordId'], api_url, creds)
            # There is a small chance that this library was sequenced directly without pooling
            unpooled_runs = get_runs(library['recordId'], api_url, creds)
            if len(unpooled_runs) > 0:
                runs = runs + unpooled_runs
            for run in runs:
                flowcell_id = run['fields']['FlowcellId']
                # Skip this flowcell if we already found it via a previous library lookup
                if flowcell_id and flowcell_id not in flowcells[library_id]:
                    flowcells[library_id].append(flowcell_id)
                    collab_id = library['fields']['OtherSampleId']
                    fastq_glob = '/ifs/archive/GCL/hiseq/FASTQ/*' + flowcell_id + '*/*' + request_id.lstrip('0') + '/*' + collab_id + '*'
                    fastq_dirs = glob(fastq_glob)
                    # ::TODO:: Check the SeqAnalysisSampleQC records to determine if a FASTQ should have been here or not
                    if len(fastq_dirs) > 0:
                        # Use only the latest sample-level subdirectory if more than 1 is found
                        fastq_dir = max(fastq_dirs, key = os.path.getctime)
                        # Use the run ID from the folder names, since that can be more reliable than whats in the LIMS
                        run_id = filter(lambda x : flowcell_id in x, fastq_dir.split('/'))[0]
                        # Find out if the FASTQs in there are paired-end or not
                        fastqs = glob(fastq_dir + '/*.fastq.gz')
                        pe_or_sr = 'PE' if [s for s in fastqs if 'R2_001.fastq.gz' in s] else 'SR'
                        # ::NOTE:: Some R code in pipelines transform '-' in sample IDs into '_', which can break steps
                        # downstream; so tweak sample ID if it contains '-' or if it does not already start with an 's_'
                        if not collab_id.startswith('s_'):
                            collab_id = 's_' + collab_id
                        if '-' in collab_id:
                            collab_id = collab_id.replace('-', '_')
                        bic_mapping.append('\t'.join(['_1', collab_id, run_id, fastq_dir, pe_or_sr]))

    mapping_file = os.path.join(args.out_dir, 'Proj_' + request_id + '_sample_mapping.txt')
    with open(mapping_file, 'w') as map_fh:
        map_fh.write('\n'.join(bic_mapping) + '\n')