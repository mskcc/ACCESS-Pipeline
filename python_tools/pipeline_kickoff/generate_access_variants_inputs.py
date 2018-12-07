import os
import re
import logging
import argparse
import ruamel.yaml

import pandas as pd

from ..constants import RUN_FILES_PATH, RUN_PARAMS_PATH


##########
# Pipeline Inputs generation for the ACCESS-Variants pipeline
#
# Todo:
# - better way to ensure proper sort order of samples
# - combine this with ACCESS-Pipeline
# - singularity


# Regex for finding bam files
BAM_REGEX = re.compile('.*\.bam')
# Delimiter for printing logs
DELIMITER = '\n' + '*' * 20 + '\n'
# Delimiter for inputs file sections
INPUTS_FILE_DELIMITER = '\n\n' + '# ' + '--' * 30 + '\n\n'

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)
logger = logging.getLogger('access_variants_pipeline_kickoff')


def parse_arguments():
    """
    Parse arguments for Variant calling pipeline inputs generation

    :return: argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_file_name', help='Filename for yaml file to be used as pipeline inputs', required=True)
    parser.add_argument('-m', '--matched_mode', action='store_true', help='Create inputs from matched T/N pairs (True), or use default Normal (False)', required=False)
    parser.add_argument('-p', '--pairing_file_path', help='tsv file with tumor sample IDs mapped to normal sample IDs', required=True)
    parser.add_argument('-dn', '--default_normal_path', help='Normal used in unmatched mode, or in matched mode if no matching normal found for tumor sample', required=True)
    parser.add_argument('-tb', '--tumor_bams_directory', help='Directory that contains all tumor bams to be used in variant calling', required=True)
    parser.add_argument('-nb', '--normal_bams_directory', help='Directory that contains all normal bams to be used in variant calling and genotyping '
                                                               '(if using matched mode, otherwise only used for genotyping)', required=True)
    parser.add_argument('-gb', '--genotyping_bams_directory', help='Directory that contains any additional bams to be used for genotyping', required=True)
    args = parser.parse_args()
    return args


def parse_tumor_normal_pairing(pairing_file, default_normal_path, tumor_samples, normal_samples, matched=True):
    """
    Build tumor-normal pairs from pairing file and tumor / normal bam directories.

    Default to `default_normal_path` if matched normal not found.

    :param path:
    :return:
    """
    ordered_tumor_samples = []
    ordered_normal_samples = []
    ordered_fillout_samples = []

    for i, tn_pair in pairing_file.iterrows():
        tumor_id = tn_pair['tumor_id']
        normal_id = tn_pair['normal_id']

        # Find the path to the bam that contains this tumor sample ID
        tumor_sample = filter(lambda t: tumor_id in t, tumor_samples)

        # Should only find one match
        assert len(tumor_sample) == 1
        tumor_sample = tumor_sample[0]

        if not matched:
            # Use default normal for all tumor samples
            ordered_tumor_samples.append(tumor_sample)
            ordered_normal_samples.append(default_normal_path)

            ordered_fillout_samples.append(tumor_sample)
            # Matched normal will still be used for genotyping (if found)
            normal_sample = filter(lambda n: normal_id in n, normal_samples)
            if len(normal_sample) == 1:
                ordered_fillout_samples.append(normal_sample[0])
            else:
                logger.warn(DELIMITER + 'Warning: Matched Normal for sample {} not found. '
                            'Skipping matched normal genotyping for this sample.'.format(tumor_id))

        elif any(normal_id in n for n in normal_samples):
            # Find the path to the matching normal bam that contains this normal sample ID
            normal_sample = filter(lambda n: normal_id in n, normal_samples)

            # Should only find one match
            assert len(normal_sample) == 1
            normal_sample = normal_sample[0]

            ordered_tumor_samples.append(tumor_sample)
            ordered_normal_samples.append(normal_sample)
            # Add both matched bams to genotyping list
            ordered_fillout_samples.append(tumor_sample)
            ordered_fillout_samples.append(normal_sample)

        else:
            # Matching normal not found, use default normal
            logger.warn(DELIMITER + 'Warning: missing paired normal for tumor sample {}'.format(tumor_sample))
            logger.warn('Pairing with default normal.')

            ordered_tumor_samples.append(tumor_sample)
            ordered_normal_samples.append(default_normal_path)
            # Only add tumor bam to genotyping list
            ordered_fillout_samples.append(tumor_sample)

    return ordered_tumor_samples, ordered_normal_samples, ordered_fillout_samples


def create_inputs_file(args):
    """
    Create the inputs.yaml file for the ACCESS Variant calling pipeline (modules 3 + 4)

    :param args: argparse.ArgumentParser object
    """
    fh = open(args.output_file_name, 'w')
    write_yaml_bams(fh, args)
    include_file_resources(fh, RUN_FILES_PATH)
    include_run_params(fh, RUN_PARAMS_PATH)
    fh.close()


def write_yaml_bams(fh, args):
    """
    Write the lists of tumor and normal bams to the inputs file

    :param fh: inputs file file handle
    :param args: argparse.ArgumentParser object with bam directory attribute
    :return:
    """
    pairing_file = pd.read_csv(args.pairing_file_path, sep='\t', header='infer')

    tumor_bam_paths = find_bams_in_directory(args.tumor_bams_directory)
    normal_bam_paths = find_bams_in_directory(args.normal_bams_directory)
    genotyping_bam_paths = find_bams_in_directory(args.genotyping_bams_directory)

    ordered_tumor_samples, ordered_normal_samples, ordered_tn_genotyping_samples = parse_tumor_normal_pairing(
        pairing_file,
        args.default_normal_path,
        tumor_bam_paths,
        normal_bam_paths,
        matched=args.matched_mode
    )

    tumor_bams = create_yaml_file_objects(ordered_tumor_samples)
    normal_bams = create_yaml_file_objects(ordered_normal_samples)

    tumor_sample_ids = [t for t in pairing_file['tumor_id']]
    if hasattr(args, 'matched'):
        # Use pairing file for matched normal sample IDs
        normal_sample_ids = [n for n in pairing_file['normal_id']]
    else:
        # Use default normal for normal sample IDs
        # Todo: Better way of doing this
        normal_sample_ids = [args.default_normal_path.split('/')[-1].split('_cl_aln')[0]] * len(tumor_sample_ids)


    genotyping_bams = create_yaml_file_objects(genotyping_bam_paths)
    # Also genotype the T/N samples that were initially used for variant calling
    tn_genotyping_bams = create_yaml_file_objects(ordered_tn_genotyping_samples)
    genotyping_bams = tn_genotyping_bams + genotyping_bams

    tumor_bam_paths = {'tumor_bams': tumor_bams}
    normal_bam_paths = {'normal_bams': normal_bams}
    tumor_sample_ids = {'tumor_sample_names': tumor_sample_ids}
    normal_sample_ids = {'normal_sample_names': normal_sample_ids}
    genotyping_bams_paths = {'genotyping_bams': genotyping_bams}

    # Write them to the inputs yaml file
    fh.write(ruamel.yaml.dump(tumor_bam_paths))
    fh.write(ruamel.yaml.dump(normal_bam_paths))
    fh.write(ruamel.yaml.dump(tumor_sample_ids))
    fh.write(ruamel.yaml.dump(normal_sample_ids))
    fh.write(ruamel.yaml.dump(genotyping_bams_paths))


def include_file_resources(fh, file_resources_path):
    """
    Write the paths to the resource files that the pipeline needs into the inputs yaml file.

    :param: fh File Handle to the inputs file for the pipeline
    :param: file_resources_path String representing full path to our resources file
    """
    with open(file_resources_path, 'r') as stream:
        file_resources = ruamel.yaml.round_trip_load(stream)

    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(file_resources))


def include_run_params(fh, run_params_path):
    """
    Load and write our default run parameters to the pipeline inputs file

    :param fh: File Handle to the pipeline inputs yaml file
    :param run_params_path:  String representing full path to the file with our default tool parameters for this run
    """
    with open(run_params_path, 'r') as stream:
        other_params = ruamel.yaml.round_trip_load(stream)

    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(other_params))


def find_bams_in_directory(dir):
    """
    Filter to just bam files found in `dir`

    :param dir: string - directory to be searched
    :return:
    """
    files_found = os.listdir(dir)
    bams_found = [os.path.join(dir, f) for f in files_found if BAM_REGEX.match(f)]
    return bams_found


def create_yaml_file_objects(bam_paths):
    """
    Turn a list of paths into a list of cwl-compatible and ruamel-compatible file objects.

    Additionally, sort the files in lexicographical order.

    :param bam_names: file basenames
    :param folder: file folder
    :return:
    """
    yaml_file_objects = []
    for b in bam_paths:
        yaml_file_object = {'class': 'File', 'path': b}
        yaml_file_objects.append(yaml_file_object)

    return yaml_file_objects


def main():
    args = parse_arguments()
    create_inputs_file(args)


if __name__ == '__main__':
    main()
